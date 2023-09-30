#chat app with group dynamic
from urllib.parse import parse_qs
from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from chat.models import Message
import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import User,UserProfile
from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.http import HttpRequest

####################################### Async##############

class MyASyncConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        print('websocket connected...',event)
        print('channel name...',self.channel_name)

        # add chanel to a new existing group static
        self.id = self.scope['url_route']['kwargs']['user_id']
        sender_id = self.scope['url_route']['kwargs']['sender_id']

        print('which user received id',self.id)
        print('which user sender id',sender_id)

        user_ids = sorted([str(self.id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"


        await self.channel_layer.group_add(gname,self.channel_name)
        await self.send({
            'type':'websocket.accept'
        })
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


    async def websocket_receive(self,event):
        self.id = self.scope['url_route']['kwargs']['user_id']
        sender_id = self.scope['url_route']['kwargs']['sender_id']
        user_ids = sorted([str(self.id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"
        
        message_data = json.loads(event['text'])
        message_content = message_data.get('message', '')
        
        if message_content:
            await self.save_message(message_content, self.id, sender_id)

        print('messege received form clinet...',event['text'])
        await self.channel_layer.group_send(gname,{
            'type' : 'chat.message',
            'message' : event['text'],

        })
    @database_sync_to_async   
    def save_message(self, message_content, sender_username, receiver_username):
        try:
            sender = User.objects.get(id=receiver_username)
            receiver = User.objects.get(id=sender_username)

            # Save the message to the database asynchronously
            message = Message(sender=sender, recipient=receiver, content=message_content)
            message.save()
        except User.DoesNotExist:
            pass
        


    async def chat_message(self,event):
        await self.send({
            'type':'websocket.send',
            'text': event['message'],
        })


    async def websocket_disconnect(self,event):
        print('websocket disconnected...',event)
        self.id = self.scope['url_route']['kwargs']['user_id']
        sender_id = self.scope['url_route']['kwargs']['sender_id']
        user_ids = sorted([str(self.id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"
        await self.channel_layer.group_discard(gname,self.channel_name)
        raise StopConsumer
    
#####################################API
class apiMyASyncConsumer(AsyncConsumer):
    @sync_to_async
    def authenticate_with_token(self, token):
        jwt_authentication = JWTAuthentication()
        dummy_request = HttpRequest()
        dummy_request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}' 
        return jwt_authentication.authenticate(dummy_request)
    
    async def websocket_connect(self,event):
        print('websocket connected...',event)
        print('channel name...',self.channel_name)

        # add chanel to a new existing group static
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_parameters = parse_qs(query_string)
        

        user_id = query_parameters.get('user_id', [''])[0]
        sender_id = query_parameters.get('sender_id', [''])[0]
        
            
        user_ids = sorted([str(user_id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"

        await self.channel_layer.group_add(gname,self.channel_name)
        print("1")
        if not user_id or not sender_id:
            await self.channel_layer.group_discard(gname,self.channel_name)
            raise StopConsumer
        print(user_id,sender_id)

        is_user_logged_in = await self.is_user_online(user_id)
        is_sender_logged_in = await self.is_user_online(sender_id)
        
        print("16--",is_user_logged_in,is_sender_logged_in)

        if not is_user_logged_in or not is_sender_logged_in:
            await self.channel_layer.group_discard(gname,self.channel_name)
            raise StopConsumer
    
        print("17")
        
        user_ids = sorted([str(user_id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"
        try:
            token = query_parameters.get('token', [''])[0]
            user, _ = await self.authenticate_with_token(token)
            if user is not None:
                print(user.id,sender_id)
                if user.id==int(sender_id):
                    gname = f"chat_{user_id}_{sender_id}"
                    await self.channel_layer.group_add(gname, self.channel_name)
                    await self.send({
                        'type': 'websocket.accept'
                    })
            else:
                await self.channel_layer.group_discard(gname,self.channel_name)
                raise StopConsumer
        except exceptions.AuthenticationFailed:
            await self.channel_layer.group_discard(gname,self.channel_name)
            raise StopConsumer
        
        

    async def websocket_receive(self,event):
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_parameters = parse_qs(query_string)
        

        user_id = query_parameters.get('user_id', [''])[0]
        sender_id = query_parameters.get('sender_id', [''])[0]
        
        user_ids = sorted([str(user_id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"
        
        message_data = json.loads(event['text'])
        message_content = message_data.get('message', '')
        
        if message_content:
            await self.save_message(message_content,user_id,sender_id)

        print('messege received form clinet...',event['text'])
        await self.channel_layer.group_send(gname,{
            'type' : 'chat.message',
            'message' : event['text'],

        })
    @database_sync_to_async   
    def save_message(self, message_content, sender_username, receiver_username):
        try:
            sender = User.objects.get(id=receiver_username)
            receiver = User.objects.get(id=sender_username)

            # Save the message to the database asynchronously
            message = Message(sender=sender, recipient=receiver, content=message_content)
            message.save()
        except User.DoesNotExist:
            pass
        


    async def chat_message(self,event):
        await self.send({
            'type':'websocket.send',
            'text': event['message'],
        })


    async def websocket_disconnect(self,event):
        print('websocket disconnected...',event)
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_parameters = parse_qs(query_string)
        

        user_id = query_parameters.get('user_id', [''])[0]
        sender_id = query_parameters.get('sender_id', [''])[0]
        
        user_ids = sorted([str(user_id), str(sender_id)])
        gname=f"chat_{user_ids[0]}_{user_ids[1]}"
        await self.channel_layer.group_discard(gname,self.channel_name)
        raise StopConsumer
    
    @sync_to_async
    def is_user_online(self, user_id):
        try:
            user_profile = UserProfile.objects.get(user_id=user_id, online=True)
            return True
        except UserProfile.DoesNotExist:
            return False