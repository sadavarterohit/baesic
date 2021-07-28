import discord
import re 
import baesic
from dotenv import load_dotenv
import os
load_dotenv()


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        txt=message.content
        
        if(txt.startswith("!solve")):
            x = re.search("```.*```", txt)
            if x:
                a=x.span()
                solve=txt[a[0]+3:a[1]-3]
                result, error = baesic.run('stdin',solve)
                if error : 
                    await message.channel.send(error.as_string())
                elif result:
                    if len(result.elements) ==1:
                        await message.channel.send(repr(result.elements[0]))
                    else:
                        await message.channel.send(repr(result))
                    


                print(solve)

client = MyClient()

token = os.getenv("Token")
print(token)
client.run(token)

    
    
    
