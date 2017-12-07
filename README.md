# Q&A Training Client

This is a simple client for a swergio set-up to generate questions and give appropriate feedback to received answers. 

Currently, the Q&A trainer just generates simple calculation Question (e.g. "What is seven plus one?"). Other possible Q&A generators can be implemented by extending the "QAGenerator" list.

The client determines the reward for a presented answer based on the similarity to the expected answer by comparing both strings. 
The client will ask the next question when the provided answer is convincing enough (similarity above a certain threshold) or a maximum amount of wrong answers was given.

The default values for the minimum similarity ratio  of  transmitted and expected answer and the maximum of possible wrong answers are:
    MIN_LIKELY_ANSWER = 1.0
    MAX_WRONG_ANSWERS = 30
These settings can be adjusted by defining environment variables.

The values for the rewards can also be specified as environment variables.
The maximum reward for the case of a fully matching answer as MAX_REWARD (Default 100). 
The reward/cost if the client can not handle the message (e.g. type is QUESTION)  as CANTHANDLE_REWARD (Default -50). 
And the reward/cost for producing the maximum of wrong answers as MAX_WRONG_ANSWER_REWARD (Default -100). 

To use a custom settings file, add the file path as environment variable CUSTOM_SETTINGS_PATH.

To start the worker just execute the "run.py" file. 