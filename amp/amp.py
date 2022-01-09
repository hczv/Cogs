from requests.models import ProtocolError
from requests.sessions import Session
from redbot.core import commands
import json
from types import SimpleNamespace
from prettytable import PrettyTable
import aiohttp

# cd into folder where cred is
import sys
sys.path.append('/data')

import cred

class amp(commands.Cog):
    """Application Management Panel (AMP) discord Integration"""

    def __init__(self, bot):
        self.bot = bot
        self.ADS_IP = str(cred.ads_host)
        self.ADS_PORT = int(cred.ads_port)
        self.ADS_PROTO = str(cred.ads_proto)
        self.ADS_username = str(cred.ads_username)
        self.ADS_password = str(cred.ads_password)
        self.ADS_INSTANCES = "PLACEHOLDER"
        self.API_HEADER = {'Accept': 'text/javascript'}
        self.session = aiohttp.ClientSession(headers=self.API_HEADER)
        self.api_get_instances = "/API/ADSModule/GetInstances"
        self.api_get_status = "/API/Core/GetStatus"
        self.api_game_start = "/API/Core/Start"
        self.api_game_stop = "/API/Core/Stop"
        self.api_game_kill = "/API/Core/Kill"
        self.api_sessions = {}
        self.api_sessions[8080] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8081] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8082] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8083] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8084] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8085] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8086] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8087] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8088] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        self.api_sessions[8089] = {'SESSIONID': '00000000-0000-0000-0000-000000000000'}
        
    @commands.group()
    async def g(self, ctx: commands.Context):
        # CREATE G COMMAND
        pass

    @g.command()
    async def list(self, ctx):
        """Lists AMP game instances"""
        table = await self.api_instance_management(0, "table")
        await ctx.send(table)

    @g.command()
    async def start(self, ctx, ID : int):
        """Starts game server"""
        PORT = await self.api_instance_management(ID, "port")
        await self.api_request(PORT, self.api_game_start)

    @g.command()
    async def stop(self, ctx, ID : int):
        """Stops game server"""
        PORT = await self.api_instance_management(ID, "port")
        await self.api_request(PORT, self.api_game_stop)

    @g.command()
    async def kill(self, ctx, ID : int):
        """Kills game server"""
        PORT = await self.api_instance_management(ID, "port")
        await self.api_request(PORT, self.api_game_kill)

    #@g.command()
    #async def test(self, ctx):
    #    cmd = 'pwd'
    #    await ctx.send("1")
    #    await ctx.send(os.system(cmd))
    #    await ctx.send("2")

    async def api_session(self, port):
        # LOGIN URL
        API_LOGIN="{}://{}:{}/API/Core/Login".format(self.ADS_PROTO, self.ADS_IP, port)
        # LOGIN INFO
        API_LOGIN_INFO = {"username": "{}".format(self.ADS_username),"password": "{}".format(self.ADS_password), "token": "", "rememberMe": "false"}
        # LOGIN REQUEST
        async with self.session.post(API_LOGIN, json=API_LOGIN_INFO) as r:
            s = await r.json()
        # FIX FORMATTING
        x = json.loads(json.dumps(s), object_hook=lambda d: SimpleNamespace(**d))
        # SET SESSION TOKEN
        print(port)
        self.api_sessions[port] = {"SESSIONID": x.sessionID}

    async def check_cred(self, port:int):
        # NEED TO VERIFY IF IT WORKS
        API_GET_STATUS="{}://{}:{}{}".format(self.ADS_PROTO, self.ADS_IP, port, self.api_get_status)
        json1 = self.api_sessions.get(port)
        async with self.session.post(API_GET_STATUS, json=json1) as r:
            STATUS1 = await r.json()
        STATUS1 = json.loads(json.dumps(STATUS1), object_hook=lambda d: SimpleNamespace(**d))
        if hasattr(STATUS1, 'Title'):
            if STATUS1.Title == "Unauthorized Access":
                await self.api_session(port)
        
    async def api_request(self, port, api):
        await self.check_cred(port)
        API_REQUEST="{}://{}:{}{}".format(self.ADS_PROTO, self.ADS_IP, port, api)
        REQUEST = ""
        try:
            async with self.session.post(API_REQUEST, json=self.api_sessions.get(port)) as r:
                REQUEST = await r.json()
            return REQUEST
        except:
            return REQUEST
 
    async def api_instance_management(self, ID:int, request):
        #if self.ADS_INSTANCES == "PLACEHOLDER":
        instances = await self.api_request(self.ADS_PORT, self.api_get_instances)
        self.ADS_INSTANCES = instances['result'][0]
        if request == "table":
            table = PrettyTable(['ID', 'Server Name', 'Port', 'Status'])
            ID = 0
            for x in self.ADS_INSTANCES.get('AvailableInstances'):
                ID += 1
                status = await self.api_request(x['Port'], self.api_get_status)
                if status['State'] == 0:
                    state = "OFF"
                elif status['State'] == 10:
                    state = "Starting"
                elif status['State'] == 20:
                    state = "Running"
                elif status['State'] == 40:
                    state = "Shutting down"
                elif status['State'] == 100:
                    state = "Killed"
                else:
                    state = status['State']
                table.add_row([ID, x['InstanceName'], x['Port'], state])
            return table
        elif request == "instance":
            return self.ADS_INSTANCES
        elif request == "port":
            ID2 = 0
            port = 0
            for x in self.ADS_INSTANCES.get('AvailableInstances'):
                ID2 += 1
                if ID2 == ID:
                    port = x['Port']
            if port != 0:
                return port