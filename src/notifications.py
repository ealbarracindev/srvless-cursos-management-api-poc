# src/utils/notifications.py

import os
import requests
from src.logs import logger

class Notification:

    def __init__(self, slack_webhookUrl=None, teams_webhookUrl=None):
        self.slack_webhookUrl = slack_webhookUrl or os.getenv("SLACK_WEBHOOK_URL")
        if not self.slack_webhookUrl:
            raise EnvironmentError("La variable de entorno 'SLACK_WEBHOOK_URL' no está configurada")
        self.teams_webhookUrl = teams_webhookUrl or os.getenv("TEAMS_WEBHOOK_URL")
        
        if not self.teams_webhookUrl:
            raise EnvironmentError("La variable de entorno 'TEAMS_WEBHOOK_URL' no está configurada")


    def send_slack_notification(self, message, channel='default'):
        payload = {"text": message}
        logger.info("slack webhook: %s", self.slack_webhookUrl)
        response = requests.post(self.slack_webhookUrl, json=payload)
        response.raise_for_status()
        

    def send_teams_notification(self, message, channel='default'):
        payload = {"text": message}
        logger.info("teams webhook: %s", self.teams_webhookUrl)
        response = requests.post(self.teams_webhookUrl, json=payload)
        response.raise_for_status()

    def send_notification(self, platform, message, channel='default'):
        if platform.lower() == 'slack':
            self.send_slack_notification(message, channel)
        elif platform.lower() == 'teams':
            self.send_teams_notification(message, channel)
