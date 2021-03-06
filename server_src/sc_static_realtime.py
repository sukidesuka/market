import script_manager
import binance
import datacenter
import json
import asyncio


class Script(script_manager.Script):
    def info(self):
        info = script_manager.ScriptInfo()
        info.title = '接收交易所的实时静态数据'
        info.description = """
        虽然是静态数据，交易所不提供websocket进行推送
        但是这个数据也具有一定的实时性
        例如每个交易对的资金费率
        一般1分钟更新一次
        """
        return info

    def main(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._main())
        loop.run_forever()

    async def _main(self):
        self.binance = await binance.create_operator()
        self.client = await datacenter.create_client()

        while True:
            premium = await self.binance.request('fapi', '/fapi/v1/premiumIndex', 'GET', {})
            for e in premium:
                symbol = e['symbol']
                rate = float(e['lastFundingRate'])
                server_time = e['time']
                asyncio.create_task(self.client.update({'premium', 'fundingRate', symbol}, rate, server_time))

            await asyncio.sleep(60)
