from .base import TPLinkRouterBase
import hashlib


# Support for EAP115


# /data/monitor.ap.aplist.json?operation=load 
# /data/monitor.ap.devinfo.json?operation=read&apMac=XXX 
# /data/monitor.ap.wsetting.json?operation=read&radioId=0&apMac=XXX 
# /data/monitor.ap.laninfo.json?operation=read&apMac=XXX 
# /data/monitor.ap.client.json?operation=load&apMac=XXX 
# /data/monitor.ap.interface.json?operation=read&interface=LAN&apMac=XXX 
# /data/monitor.ap.interface.json?operation=read&interface=WIFI0&apMac=XXX 
# /data/monitor.client.client.json?operation=load 
# /data/monitor.client.portaluser.json?operation=load 
# /data/sysmod.json?operation=read 
# /data/syslogShow.json

PATH_CLIENT_LIST = '/data/monitor.client.client.json'
PATH_AP_LIST = '/data/monitor.ap.aplist.json'
PATH_DEV_INFO = '/data/monitor.ap.devinfo.json'
PATH_AP_LAN_INFO = '/data/monitor.ap.laninfo.json'


class TPLinkEAP(TPLinkRouterBase):
    def _make_login_params(self, cookies):
        password_md5 = hashlib.md5(
            self.password.encode("utf")).hexdigest().upper()
        login_data = {"username": self.username, "password": password_md5}

        return login_data

    async def clients(self):
        clients = await self.get_data(PATH_CLIENT_LIST, operation='load')

        # fixup some things
        for c in clients:
            c['MAC'] = c['MAC'].replace("-", ":")

        return clients

    async def access_points(self):
        aps = await self.get_data(PATH_AP_LIST, operation='load')

        return aps

    async def ap_lan_info(self, ap_mac=None):
        # use first AP MAC if none given
        ap_mac = ap_mac if ap_mac else (await self.access_points())[0]['MAC']

        info = await self.get_data(PATH_AP_LAN_INFO, operation='read', apMac=ap_mac)

        return info

    async def device_info(self, ap_mac=None):
        # use first AP MAC if none given
        ap_mac = ap_mac if ap_mac else (await self.access_points())[0]['MAC']

        aps = await self.get_data(PATH_DEV_INFO, operation='read', apMac=ap_mac)

        return aps


async def main():
    import json

    with open("../secrets_tpl.json") as handle:
        login = json.load(handle)
        
    tpl = await TPLinkEAP('192.168.0.21', **login).login()

    clients = await tpl.clients()
    print(json.dumps(clients, indent='  '))

    device_info = await tpl.device_info()
    print(json.dumps(device_info, indent='  '))

    ap_lan_info = await tpl.ap_lan_info()
    print(json.dumps(ap_lan_info, indent='  '))

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
