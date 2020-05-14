import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from fuzzywuzzy import fuzz


# synchronous WebSocket consumer
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']  # see ./routing.py:6
        self.room_group_name = f'chat_{self.room_name}'

        # The async_to_sync(…) wrapper is required because ChatConsumer is a synchronous WebsocketConsumer but it is
        # calling an asynchronous channel layer method. (All channel layer methods are asynchronous.)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        # Accepts the WebSocket connection.
        # If you do not call accept() within the connect() method then the connection will be rejected and closed.
        #   You might want to reject a connection for example because the requesting user is not authorized to perform
        #   the requested action.
        # It is recommended that accept() be called as the last action in connect() if you choose to accept the
        #   connection.
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        message = json_data['message']

        # send message to room_group
        # An event has a special 'type' key corresponding to the name of the method that should be invoked on
        #   consumers that receive the event.
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                'type': 'chat_message',
                'message': message,
            }
        )

    def chat_message(self, event):
        message = event['message']

        # send message to WebSocket
        self.send(text_data=json.dumps({
            'message': f'[{self.room_name}] {message}'
        }))


class HelpConsumer(WebsocketConsumer):
    question_dict = {
                    'title': 'Deep Questions To Ask In Your Journal',
                    'questions': [
                        'What are you most likely very wrong about',
                        'What chapters would you separate your autobiography into',
                        'What are some things you’ve had to unlearn',
                        'What could you give a 40-minute presentation on with absolutely no preparation',
                        'What question would you most like to know the answer to',
                        'If you didn’t have to sleep, what would you do with the extra time',
                        'Why did you decide to do what you are doing now in your life',
                        'What’s the best and worst piece of advice you’ve ever received',
                        'What’s the most impactful ‘no’ you’ve said recently',
                        'What was the most stressful experience of your life',
                    ]
                }, {
                    'title': 'Deep Questions To Get To Know Yourself',
                    'questions': [
                        'Is there something that you’ve dreamt of doing for a long time',
                        'What would you like to change about your family',
                        'What was a place or event that transformed your ideas, thinking, perspective, or made you come alive in a new way',
                        'What one thing you would do if it would be impossible to fail',
                        'What is something you love now, that you never could have imagined you would like in the past',
                        'If you could invite anyone, living or dead to dinner, who would that be and why',
                        'If a crystal ball could tell you the truth about yourself, your life, the future or anything else, what would you want to know',
                        'What are you addicted to',
                        'What’s the milestone you’re working towards right now in your personal and professional life',
                        'What was the most bizarre encounter you’ve had in your life',
                    ]
                }, {
                    'title': 'Deep Questions To Find Your Lifes Purpouse',
                    'questions': [
                        'If you were to die this evening with no opportunity to communicate with anyone, what would you most regret not having told someone',
                        'What do you spend too much time doing',
                        'What don’t you spend enough time doing',
                        'What makes you feel most alive',
                        'What is something you know you do differently than most people',
                        'What advice would you offer to yourself five years ago',
                        'What small gesture from a stranger made a big impact on you',
                        'What are you looking forward to in the coming months',
                        'Did you ever feel lost in your life path',
                        'What do you want your epitaph to be',
                        'What do you regret not doing',
                    ]
                }, {
                    'title': 'Deep Questions To Find Your Soul',
                    'questions': [
                        'What would constitute a perfect day for you',
                        'What’s something you love about yourself',
                        'When do you feel truly alive',
                        'When people come to you for help, what do they usually want help with',
                        'What do you consider as your biggest achievement in the last 5 years',
                        'What is the most challenging part of your job',
                        'What was a major turning point in your life',
                        'What’s one thing that could happen today that would make it great',
                        'If you knew that in one year you would die suddenly, would you change anything about the way you are now living',
                        'What would you like to ask yourself',
                    ]
                }

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        user_question = json_data['question']
        fuzz_ratio_high = 0
        fuzz_ratio_highest = ''

        # 1. find fuzz ratio among the questions
        # 2. return the highest ratio to the user
        # 2a maybe #2 and #3 also?
        # 3. Unless there is a 100% match
        # for ... else
        # for question in questions:
        #     if fuzz.ratio(question, user_question) == 100:
        #         # Found it!
        #         process(item) // return the user_question
        #         break
        # else:
        #     # Didn't find anything..
        #     not_found_in_container() // did you mean (highest fuzz-ratio 1,2,3)

        for question_category in self.question_dict:
            for question in question_category['questions']:
                fuzz_ratio = fuzz.ratio(question, user_question)
                if fuzz_ratio == 100:
                    self.send(text_data=json.dumps({
                        'question': user_question,
                        'message': 'Which is one of the essential Deep Questions, think about that!',
                        'fuzz_ratio': fuzz_ratio,
                        'category': question_category['title'],
                    }))
                    break
                else:
                    if fuzz_ratio > fuzz_ratio_high:
                        fuzz_ratio_high = fuzz_ratio
                        fuzz_ratio_highest = question
            else:
                self.send(text_data=json.dumps({
                    'question': user_question,
                    'message': fuzz_ratio_highest,
                    'fuzz_ratio': fuzz_ratio_high,
                    'category': question_category['title'],
                }))
                fuzz_ratio_high = 0
                fuzz_ratio_highest = ''
