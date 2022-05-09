#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

import requests

# Import logging library
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source

# from requests.api import request


class SourceEmploymentHero(Source):
    global refresh_token
    refresh_token = None

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:

        try:
            # Connection CHECK
            level_obj = "organization"
            url = self._get_url(config, level_obj)
            r = self._make_request(config, url)
            # stream_name = 'teams'
            # r = self._get_obj_data(config, stream_name)
            # print(r)
            if r.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred in the CHECK: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:

        streams = []

        schema = self._get_obj_schema(config)
        for key, values in schema.items():
            stream_name = key
            modes = ["full_refresh", "incremental"]
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": True,
                "type": "object",
                "properties": values,
            }

            streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes=modes))
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:

        config_stream_names = []
        for configured_stream in catalog.streams:
            stream_name = configured_stream.stream.name
            config_stream_names.append(stream_name)
            # print(f'STREAM NAME IS: {stream_name}')

            level_data = self._get_obj_data(config, stream_name)
            for record in level_data:
                record_data = record
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=record_data, emitted_at=int(datetime.now().timestamp()) * 1000),
                )

    def _get_obj_data(self, config, level):
        level_data = []
        try:
            level_url = self._get_url(config, level)
            r = self._make_request(config, level_url)
        except Exception as err:
            print(f"Error with object {level} wxith _make_request() in _get_obj_schema : {err}")
        level_obj = r.json()
        for data in level_obj["data"]["items"]:
            dicts = {k: v for (k, v) in data.items()}
            level_data.append(dicts)
        return level_data

    def _get_obj_schema(self, config):
        schema = {}
        level_list = ["organization", "teams", "employee"]
        # level_list = ['teams']

        for level in level_list:
            try:
                level_url = self._get_url(config, level)
                r = self._make_request(config, level_url)
            except Exception as err:
                print(f"Error with object {level} with _make_request() in _get_obj_schema : {err}")
            level_obj = r.json()
            level_obj_schema = level_obj["data"]["items"][0]  # First obj doesnt necessary
            level_schema = {k: {"type": "string"} for (k, v) in level_obj_schema.items()}
            schema[level] = level_schema
        return schema

    def _get_org_id(self, config):
        level_obj = "organization"
        url = self._get_url(config, level_obj)
        r = self._make_request(config, url)
        org_obj = r.json()
        org_id = org_obj["data"]["items"][0]["id"]
        return org_id

    def _get_url(self, config, level_obj):

        if level_obj == "organization":
            org_url = "https://api.employmenthero.com/api/v1/organisations"
            return org_url
        elif level_obj == "teams":
            org_id = self._get_org_id(config)
            team_url = f"https://api.employmenthero.com/api/v1/organisations/{org_id}/teams"
            # print(team_url)
            return team_url
        elif level_obj == "employee":
            org_id = self._get_org_id(config)
            emp_url = f"https://api.employmenthero.com/api/v1/organisations/{org_id}/employees"
            return emp_url

    def _make_request(self, config, url):

        if refresh_token is not None:
            token = refresh_token
        else:
            token = self._get_access_token(config)
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
        except Exception as err:
            print(f"Error with request.get() in _make_request : {err}")
        return response

    def _get_access_token(self, config):

        ID = config.get("client_id")
        SECRET = config.get("client_secret")
        CALLBACK = config.get("callback")
        AUTH = config.get("authorization_code")

        # ACCESS TOKEN
        url = f"https://oauth.employmenthero.com/oauth2/token?client_id={ID}&client_secret={SECRET}&grant_type=authorization_code&code={AUTH}&redirect_uri={CALLBACK}"
        response = requests.post(url)
        content = response.text
        access_obj = json.loads(content)
        TOKEN = access_obj["access_token"]
        REFRESH = access_obj["refresh_token"]
        # headers = {"Authorization": f"Bearer {TOKEN}"}

        url = f"https://oauth.employmenthero.com/oauth2/token?client_id={ID}&client_secret={SECRET}&grant_type=refresh_token&code={TOKEN}&redirect_uri={CALLBACK}&refresh_token={REFRESH}"
        response = requests.post(url)
        content = response.text
        access_obj = json.loads(content)
        # TOKEN = access_obj['access_token']
        refresh_token = access_obj["access_token"]
        # print("CALL WAS INSIDE GET ACCESS")
        return refresh_token

    def _parse_config(self, config):
        return {
            "client_id": config.get("client_id"),
            "client_secret": config.get("client_secret"),
            "callback": config.get("callback"),
            "auth_code": config.get("authorization_code"),
        }
