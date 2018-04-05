import asyncio
import pickle
from discow.utils import *
from discow.handlers import add_message_handler, flip_shutdown, get_data
from discord import Embed
import urllib.request as req
import urllib.error as err
from bs4 import BeautifulSoup

@asyncio.coroutine
def info(Discow, msg):
    em = Embed(title="Who am I?", colour=0x9542f4)
    em.description = "Hi, I'm [discow](https://github.com/UnsignedByte/discow), a discord bot created by <@418827664304898048> and <@418667403396775936>."
    em.add_field(name="Features", value="For information about my features do `"+discow_prefix+"help` or take a look at [our readme](https://github.com/UnsignedByte/discow/blob/master/README.md)!")
    yield from send_embed(Discow, msg, em)

@asyncio.coroutine
def quote(Discow, msg):
    m = yield from Discow.get_message((msg.channel if len(msg.channel_mentions) == 0 else msg.channel_mentions[0]), strip_command(msg.content).split(" ")[0])
    em = Embed(colour=0x3b7ce5)
    em.title = "Message Quoted by "+msg.author.display_name+":"
    desc = m.content
    log = yield from Discow.logs_from(m.channel, limit=20, after=m)
    log = reversed(list(log))
    for a in log:
        if a.author == m.author:
            if a.content:
                desc+="\n"+a.content
        else:
            break
    log = yield from Discow.logs_from(m.channel, limit=10, before=m)
    log = list(log)
    for a in log:
        if a.author == m.author:
            if a.content:
                desc=a.content+"\n"+desc
        else:
            break
    em.description = desc
    txt = "Written by "+m.author.display_name+" on "+convertTime(m.timestamp, m.server)
    avatarurl = m.author.avatar_url
    if not avatarurl:
        avatarurl = m.author.default_avatar_url
    em.set_footer(text=txt, icon_url=avatarurl)
    yield from Discow.delete_message(msg)
    yield from send_embed(Discow, msg, em)

@asyncio.coroutine
def dictionary(Discow, msg):
    link="https://www.merriam-webster.com/dictionary/"
    x = strip_command(msg.content).replace(' ', '%20')
    em = Embed(title="Definition for "+x+".", description="Retrieving Definition...", colour=0x4e91fc)
    dictm = yield from send_embed(Discow, msg, em)

    try:
        html_doc = req.urlopen(link+x)
        soup = BeautifulSoup(html_doc, 'html.parser')
    except err.HTTPError as e:
        try:
            em.description = "Could not find "+x+" in the dictionary. Choose one of the words below, or type 'cancel' to cancel."
            soup = BeautifulSoup(e.read(), 'html.parser')
            words = soup.find("ol", {"class":"definition-list"}).get_text().split()
            for i in range(0, len(words)):
                em.description+='\n**'+str(i+1)+":** *"+words[i]+'*'
            dictm = yield from edit_embed(Discow, dictm, em)
            while True:
                vm = yield from Discow.wait_for_message(author=msg.author)
                v = vm.content
                if v == 'cancel':
                    em.description="*Operation Canceled*"
                    dictm = yield from edit_embed(Discow, dictm, em)
                    return
                elif isInteger(v):
                    if int(v)>=1 and int(v) <=len(words):
                        x = words[int(v)-1].replace(' ', "%20")
                        yield from Discow.delete_message(vm)
                        break
                else:
                    if v in words:
                        x = v.replace(' ', "%20")
                        yield from Discow.delete_message(vm)
                        break
            html_doc = req.urlopen(link+x)
            soup = BeautifulSoup(html_doc, 'html.parser')
            em.title = "Definition for "+x+"."
            em.description = "Retrieving Definition..."
            dictm = yield from edit_embed(Discow, dictm, em)
        except AttributeError:
            em.description = "Could not find "+x+" in the dictionary."
            dictm = yield from edit_embed(Discow, dictm, em)
            return

    em.description = ""
    txts = soup.find("div", {"id" : "entry-1"}).find("div", {"class":"vg"}).findAll("div", {"class":["sb", "has-sn"]}, recursive=False)
    for x in txts:
        l = list(filter(None,map(lambda x:x.strip(), x.get_text().split("\n"))))
        st = ""
        for a in l:
            if a.startswith(":"):
                st+=' '.join(a.strip().split())
            else:
                v1 = a.split()
                if isInteger(v1[0]):
                    st+="\n**__"+v1[0]+"__**"
                    v1 = v1[1:]
                for n in v1:
                    if isInteger(n.strip("()")):
                        st+="\n\t\t***"+n+"***"
                    elif len(n)==1:
                        st+="\n\t**"+n+"**"
                    else:
                        st+=" *"+n+"*"

        em.description+= '\n'+st
    em.description+="\n\nDefinitions retrieved from [The Merriam-Webster Dictionary](https://www.merriam-webster.com/) using [Dictionary](https://github.com/UnsignedByte/Dictionary) by [UnsignedByte](https://github.com/UnsignedByte)."
    dictm = yield from edit_embed(Discow, dictm, em)


@asyncio.coroutine
def purge(Discow, msg):
    num = max(1,min(100,int(parse_command(msg.content, 1)[1])))+1
    msgs = yield from Discow.logs_from(msg.channel, limit=num)
    msgs = list(msgs)
    if num == 1:
        yield from Discow.delete_message(msgs[0])
    else:
        yield from Discow.delete_messages(msgs)
    m = yield from Discow.send_message(msg.channel, format_response("**{_mention}** has cleared the last **{_number}** messages!", _msg=msg, _number=num-1))
    yield from asyncio.sleep(2)
    yield from Discow.delete_message(m)

@asyncio.coroutine
def save(Discow, msg):
    perms = msg.channel.permissions_for(msg.author)
    if perms.manage_server:
        em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
        msg = yield from send_embed(Discow, msg, em)
        flip_shutdown()
        yield from asyncio.sleep(1)
        data = get_data()
        with open("discow/client/data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        with open("discow/client/data/user_data.txt", "wb") as f:
            pickle.dump(data[1], f)
        em.description = "Complete!"
        flip_shutdown()
        msg = yield from edit_embed(Discow, msg, embed=em)
    else:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        yield from send_embed(Discow, msg, em)

@asyncio.coroutine
def shutdown(Discow, msg):
    yield from save(Discow, msg)
    yield from Discow.logout()


add_message_handler(info, "hi")
add_message_handler(info, "info")
add_message_handler(shutdown, "close")
add_message_handler(shutdown, "shutdown")
add_message_handler(save, "save")
add_message_handler(purge, "purge")
add_message_handler(purge, "clear")
add_message_handler(quote, "quote")
add_message_handler(dictionary, "define")
add_message_handler(dictionary, "dictionary")