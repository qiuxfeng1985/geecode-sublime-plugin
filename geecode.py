import sublime
import sublime_plugin
from urllib import request
import time
import sys
import os.path
import json
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geecode_keywords
from TipDisplay import TipDisplay
import geecode_similar

def Get(url):
    with request.urlopen(url) as f:
                data = f.read()
                # if data is N
                try:
                    ret = data.decode('utf-8')
                except UnicodeDecodeError:
                    ret = "{}"
                return ret

def Post(url,data):
    # data1 = {'spam':1,'eggs':2,'bacon':0}
    headers = {'content-type': 'application/json'}
    ret = requests.post(url, data = json.dumps(data), headers = headers)
    return json.loads(ret.text)

def formatPopup(content):
        content = '''<body><pre class="exampleStr"> '''+content+''' </pre><br></br></body>'''
        return content

def getExamplePop(content):
        content =  '''<body> <pre class="exampleStr"> '''+content +'''</pre><br></br> </body> '''
        return content

class FindExampleCommand(sublime_plugin.TextCommand):
	def run(self, edit):
            if len(self.view.sel()) != 1:
                print(self.view, 'Please select only one region.')
                return
            region = self.view.sel()[0]
            showCode = '''<br><H1>&nbsp;&nbsp;&nbsp;查找例子&nbsp;&nbsp;&nbsp;</H1><br>'''
            if region.empty():
                # print(self.view, 'Selected text is empty.')
                showCode = showCode + '''Selected text is empty.\n<br>'''
            else:
                word_raw = self.view.substr(region)
                
                url = 'http://geecall.com/clientapi/ReadExamples?full_api='+word_raw
                ret = Get(url)
                examlpeArray = json.loads(ret, encoding='utf-8')
                index = 0
                exampleLength = len(examlpeArray)
                # print('exampleLength = ',exampleLength)
                if exampleLength > 0 :
                    for examlpe in examlpeArray: 
                        temp = str(index+1)
                        showCode = showCode +'''<H2>Example '''+temp + '''</H2><p></p><p></p>'''+examlpe["code"]+'''\n<br>''' 
                        index=index+1
                        if index >= 30:
                            break;
                else :
                    showCode = showCode + '''暂无例子''' + '''\n<br>'''
                showCode = repalaceCode(showCode)
            
            # showCode = markdown.markdown(showCode, extensions=['markdown.extensions.codehilite'])
            # self.view.show_popup(showCode,sublime.COOPERATE_WITH_AUTO_COMPLETE,-1,600,600)
            # print(showCode)
            TipDisplay.display(self.view,showCode)

class SmartCodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
            view = self.view
            print(time.time()," ---- Smart Code -----")
            code_string = view.substr(sublime.Region(0, view.size()))
            # print("code_string = " + code_string)
            keywords = geecode_keywords.getScanKeyWords(code_string)
            print(time.time(),"step2 ",json.dumps(keywords))
            findExamples = Post("http://geecall.com/clientapi/SearchSimilar",keywords)
            tempLen = len(findExamples)//2
            findExamples = findExamples[0:tempLen]
            findExamples.append(code_string)
            pareExample = geecode_similar.getSimilarExample(findExamples)
            examlpe = repalaceCode(pareExample[0])
            examlpe = '''<br><H1>智能提示</H1><br>'''+examlpe+'''\n<br>'''
            TipDisplay.display(view,examlpe)
            # view.show_popup(examlpe,sublime.COOPERATE_WITH_AUTO_COMPLETE,-1,600,600)
            # print(time.time(),"step5","-----display----")
            

class EnterKeyHandler(sublime_plugin.EventListener):
    def __init__(self):
            self._last_command = None
    def on_post_text_command(self,view, command_name, args):
            print("on_post_text_command",command_name)
            # if "insert" == self._last_command:
            # # if "context_menu" == self._last_command:

    def on_text_command(self, view, command_name, args):
            print("on_text_command command_name = " + command_name)
            self._last_command = command_name
            # if "insert" == self._last_command:
            # if "context_menu" == self._last_command:
            

def repalaceCode(code):
    newCode = '''<br>'''
    listCode = code.split('\n')
    for lineCode in listCode :
        if (len(lineCode) > 0 and lineCode[0] == '#') :
            lineCode = '\\'+lineCode
        newCode = newCode + lineCode + '''\n'''
    return newCode 
