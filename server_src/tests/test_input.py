import script_manager


class Script(script_manager.Script):
    def info(self):
        info = script_manager.ScriptInfo()
        info.title = '用户输入接收测试'
        info.description = '用来测试用户输入能否正常接收的脚本'
        info.inputs = []
        info.inputs.append(script_manager.ScriptInput('输入A', 'input_a', '默认A'))
        info.inputs.append(script_manager.ScriptInput('输入B', 'input_b', ''))
        return info

    def main(self):
        self.log('用户输入A为', self.input_dict['input_a'])
        self.log('用户输入B为', self.input_dict['input_b'])
