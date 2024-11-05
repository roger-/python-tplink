from .base import TPLinkRouterBase
import hashlib


# Support for CPE210 (maybe others)

PATH_DEV_INFO = '/data/info.json'
PATH_VERSION = '/data/version.json' # used for login
PATH_STATION = '/data/station.json'
PATH_INTERFACES = '/data/interfaces.json'


class TPLinkCPE(TPLinkRouterBase):
    URL_BASE = 'https://{host}'
    PATH_LOGIN = PATH_VERSION
    PATH_COOKIE = PATH_VERSION

    def _make_login_params(self, cookies):
        nonce = cookies.get('COOKIE').lower()
        password_md5 = hashlib.md5(self.password.encode("utf")).hexdigest()

        prehash = password_md5.upper() + ":" + nonce
        encoded = self.username + ":" + \
            hashlib.md5(prehash.encode("utf")).hexdigest().upper()

        login_data = {'encoded': encoded, 'nonce': nonce}

        return login_data

    async def clients(self):
        clients = await self.get_data(PATH_STATION, operation='load')

        return clients

    async def interfaces(self):
        interfaces = await self.get_data(PATH_INTERFACES, operation='load')

        return interfaces
    
    async def device_info(self):
        dev_info = await self.get_data(PATH_DEV_INFO, operation='load', id='info')

        return dev_info


async def main():
    import json

    with open("../secrets_tpl.json") as handle:
        login = json.load(handle)

    tpl = await TPLinkCPE('192.168.0.25', **login).login()

    print(json.dumps(await tpl.device_info(), indent='  '))
    print(json.dumps(await tpl.clients(), indent='  '))
    print(json.dumps(await tpl.interfaces(), indent='  '))

    await tpl.close()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
