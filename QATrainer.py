from uuid import uuid4
import time
import difflib
import os

from SwergioUtility.SocketIOClient import SocketIOClient
from SwergioUtility.MessageUtility import  MessageInterface
from SwergioUtility.Settings import getBasicSettings
from uuid import uuid4
import time

from QAGenerators.calculation import Calculation



class QATrainer():

    MAX_WRONG_ANSWERS = 30

    def __init__ (self, custom_settings_path = None):
        self._socketIONamespaces = ['QATrainer']
        self._socketIOSenderID = uuid4()
        self._socketIOClient = SocketIOClient(self._socketIONamespaces)
        
        self.QAGenerators = [Calculation()]
        self.ExpectedAnswer = ""
        self.CurrentQuestion = ""
        
        self.min_likely_answer  = os.getenv('MIN_LIKELY_ANSWER') or 1.0
        self.max_wrong_answers  = os.getenv('MAX_WRONG_ANSWERS') or 30

        self.max_reward  = os.getenv('MAX_REWARD') or 100
        self.max_wrong_answers_reward  = os.getenv('MAX_WRONG_ANSWER_REWARD') or -50
        self.canthandle_reward  = os.getenv('CANTHANDLE_REWARD') or -100

        custom_settings_path = custom_settings_path or os.getenv('CUSTOM_SETTINGS_PATH')
        max_length_message_text, self.MessageTypeEnum  = getBasicSettings(custom_settings_path)
        #wait for other components to load
        time.sleep(30)
        print('start questions')
        self.reset()
        self.wrong_answers_count = 0

    def On_QATrainer_Message(self,data):
        msg = MessageInterface.from_document(data)
        comID = msg.CommunicationID
        if msg.SenderID != str(self._socketIOSenderID):
            
            if self.MessageTypeEnum[msg.MessageType] == self.MessageTypeEnum.ANSWER:
                answer = msg.Data 
                self.act(answer,comID)
            else:
                self.canthandle(comID)
    
    def ListenToSocketIO(self):
        self._socketIOHandler = [self.On_QATrainer_Message]
        self._socketIOClient.listen(self._socketIOHandler)


    def act(self,answer,CommunicationID):
        seq = difflib.SequenceMatcher(a=self.ExpectedAnswer.lower(), b=answer.lower())
        seq_ration = seq.ratio()

        if seq_ration >= self.min_likely_answer:
            ob = "correct"
            done = True
            reward = seq_ration*self.max_reward
        else:
            ob = self.CurrentQuestion
            done = False
            reward = seq_ration*self.max_reward
            self.wrong_answers_count += 1

        if self.wrong_answers_count >= self.max_wrong_answers:
            done = True
            reward = self.max_wrong_answers_reward

        self.emitObservation(ob,reward, done, CommunicationID)
        if done:
            self.reset()

    def reset(self):
        comID = uuid4()
        qa = self.QAGenerators[0].RandomQA()
        self.ExpectedAnswer = qa[1]
        question  = qa[0]
        self.wrong_answers_count = 0
        self.CurrentQuestion = question 
        self.emitObservation(question, reward=0.0, done = False,CommunicationID = comID)

    def canthandle(self,comID):
        done = False
        if self.wrong_answers_count >= self.max_wrong_answers:
            done = True
            reward = self.max_wrong_answers_reward
        else:
            reward = self.canthandle_reward
            self.wrong_answers_count += 1
        
        question = self.CurrentQuestion
        self.emitObservation(question,reward,done,comID)
        if done:
            self.reset()

    def emitObservation(self,question,reward, done,CommunicationID):
        msgTyp = self.MessageTypeEnum.QUESTION.name
        namespace = self._socketIONamespaces[0]
        #convert observation from numpy to list and then to string
        if type(question) != str:
            if type(question)  == int:
                question = str(question)
            else:
                question = str(list(question))
        Message = MessageInterface(namespace,self._socketIOSenderID, msgTyp,CommunicationID,Data = question, Reward = reward, DoneFlag = done)
        self._socketIOClient.emit(Message,namespace)  
