import discord
from discord.ext import commands
from httpx import AsyncClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class StrawCog(commands.Cog):
    def __init__(self):
        self.httpx_client = AsyncClient()

    @commands.command()
    async def op_wiki(self, ctx, *search_term):
        """ -Returns a One Piece Wiki article"""
        if not search_term:
            await ctx.reply("Please input a search term")
            return
          
        joined_search_term = " ".join(search_term)
        joined_search_term = joined_search_term.title()
        proper_capital = ""
        for i in range(len(joined_search_term)):
            if i == 0:
                proper_capital += joined_search_term[i].upper()
            elif joined_search_term[i:i+3].upper() == "NO ":
                proper_capital += joined_search_term[i].lower()
            else:
                proper_capital += joined_search_term[i]
        joined_search_term = proper_capital
        if joined_search_term.lower() == "cp9" or joined_search_term.lower() == "cp0" or joined_search_term.lower() == "ssg":
            joined_search_term = joined_search_term.upper()
        formatted_search_term = joined_search_term.replace(' ', '_')
        url = f"https://onepiece.fandom.com/wiki/{formatted_search_term}"
        
        response = requests.get(url)
      
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for data in soup(['style', 'script']):
                # Remove tags
                data.decompose()
            
            # GETTING PRIMARY DESCRIPTION OF ARTICLE
            paragraphs = soup.find_all('p')
            first_paragraph = paragraphs[1]
            first_paragraph = str(first_paragraph)
            CLEANR = re.compile('<.*?>') 
            first_paragraph = re.sub(CLEANR,"",first_paragraph)
            first_paragraph = re.sub("[\(\[].*?[\)\]]", "", first_paragraph)
            
            # GETTING THUMBNAIL IF IT EXISTS
            image_url = None
            image_element = soup.find('img', class_='pi-image-thumbnail')
            if image_element:
                relative_image_url = image_element['src']
                image_url = urljoin(url, relative_image_url)
                
            embed=discord.Embed(title="One Piece Wiki <a:StrawHat:1108291618441789460>",description=first_paragraph,url=url, color=0xFF0000)
            embed.set_image(url=image_url)
            
            # CHECKING FOR A BOUNTY AND GETTING IT IF IT EXISTS
            bounty_element = soup.find('div', attrs={'class': 'pi-item', 'data-source': 'bounty'})
            
            current_bounty = None
            if bounty_element:
                bounty = bounty_element.text.strip()
                bounty_strip = bounty[8:]
                for i in range(len(bounty_strip)):
                    if bounty_strip[i] == "[":
                        current_bounty = bounty_strip[:i]
                        break
            
            # CHECKING FOR AGE IF ALIVE
            age_element = soup.find('div', attrs={'class': 'pi-item', 'data-source': 'age'})
            # CHECKING FOR AGE IF DEAD
            age2_element = soup.find('div', attrs={'class': 'pi-item', 'data-source': 'age2'})
            age = None
            if age_element and not age2_element:
                age = age_element.text.strip()
                age = age[5:]

                for i in range(len(age)):
                    if age[i:i+2].lower() == "ov":
                        age = "Over 1000"
                        break
                    if "(a" in age:
                        if age[i:i+2] == "(a":
                            age = age[i-3:i]
                            break
                    else:
                        if age[i] == "[":
                            age = age[:i]
                            break
    
            elif age2_element:
                age = age2_element.text.strip()
                age = age[14:]
                for i in range(len(age)):
                    if age[i] == "[" or age[i] == "(":
                        age = age[:i] + " (DEAD)"
                        break
                
            if current_bounty != None and age != None:
                embed.set_footer(text=f"BOUNTY: {current_bounty} | AGE: {age}",icon_url="https://cdn.discordapp.com/emojis/572643868726525952.png?v=1")
            elif current_bounty != None:
                embed.set_footer(text=f"BOUNTY: {current_bounty}",icon_url="https://cdn.discordapp.com/emojis/572643868726525952.png?v=1")
            elif age != None:
                embed.set_footer(text=f"AGE: {age}",icon_url="https://cdn.discordapp.com/emojis/868749522724085780.png?v=1")
              
            try:
                # SUCCESS
                await ctx.reply(embed=embed)
            except:
                error = "The page you requested *is* valid, but the fandom client has issues on its end preventing the request from being properly processed. You can press the hyperlink above to go directly to the article instead if you'd like. Sorry!"
                embed=discord.Embed(title="One Piece Wiki <a:StrawHat:1108291618441789460>",description=error, url=url, color=0xFF0000)
                embed.set_image(url='https://media.tenor.com/Vs9QNG3lQZUAAAAS/luffy-one-piece.gif')
                await ctx.reply(embed=embed)
        else:
            # INVALID SEARCH TERM
            embed=discord.Embed(title="One Piece Wiki <a:StrawHat:1108291618441789460>",description=f"Could not find an article for: {joined_search_term}", color=0xFF0000)
            await ctx.reply(embed=embed)
            
    @commands.command()
    async def ch_sum(self, ctx, chapter_number):
        if not chapter_number or not chapter_number.isnumeric():
            return
        
        url = f"https://onepiece.fandom.com/wiki/Chapter_{chapter_number}"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for data in soup(['style', 'script']):
                data.decompose()
        
        # GETTING PRIMARY DESCRIPTION OF ARTICLE
            paragraphs = soup.find_all('p')
            first_paragraph = paragraphs[3]
            sec_paragraph = paragraphs[4]
            first_paragraph = str(first_paragraph)
            sec_paragraph = str(sec_paragraph)
            summary = f"{first_paragraph}\n{sec_paragraph}"
            CLEANR = re.compile('<.*?>') 
            summary = re.sub(CLEANR,"",summary)
            summary = re.sub("[\(\[].*?[\)\]]", "", summary)
            
        await ctx.reply(summary)
