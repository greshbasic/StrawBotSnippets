# hey! this file is used to set up web scrapping for StrawBot's standard group of reference commands. In particular wiki and ai.
# wiki will grab and return a Wikipedia Article for the search term (if found) 
# ai will submit a user's provided prompt to ChatGPT and return ChatGPT's response

class ReferenceCog(commands.Cog):
    def __init__(self):
        self.httpx_client = AsyncClient()

    @commands.command()
    async def wiki(self, ctx, *search_term):
        """ -Returns a wikipedia article"""
        if not search_term:
            await ctx.reply("Please input a search term")
            return

        joined_search_term = " ".join(search_term)
        quoted_search_term = urllib.parse.quote(joined_search_term)
        search_result = await self.httpx_client.get(f'https://en.wikipedia.org/w/api.php?action=opensearch&search={quoted_search_term}&limit=1&namespace=0&format=json')
        results_list = json.loads(search_result.text)
        
        if len(results_list[3]) > 0:
            await ctx.reply(f"{results_list[3][0]}")
        else:
            await ctx.reply(f"`No Wikipedia article was found for: {joined_search_term}`")
    
   @staticmethod
    def add_to_history(role, content):

        if not content or not isinstance(content, str):
            return "Invalid content. Content must be a non-empty string."

        conversation_history.append({"role": role, "content": content})
        
    @staticmethod
    def chat_gpt(message):
        ReferenceCog.add_to_history("user", message)
        assistant = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=conversation_history
        )

        ReferenceCog.add_to_history("assistant", assistant['choices'][0]['message']['content'])
        response_content = assistant['choices'][0]['message']['content']

        return response_content
        
    @commands.command()
    async def ai(self, ctx, *query):
          """ -Returns ChatGPT response to given prompt"""
        for i in range(len(query)):
            if i == len(query) - 1:
                string += f"{query[i]}"
            else:
                string += f"{query[i]} "
        try:
            await ctx.message.add_reaction("<a:loading:1159345309172912178>") # a small loading circle to let user know that the command did indeed go through
            reply = ReferenceCog.chat_gpt(string)

        except Exception as e:
            await ctx.message.add_reaction("❌")
            reply = e
        
        embed=discord.Embed(title="StrawBot AI", description=reply, color=0x8717d7)
        await ctx.message.add_reaction("✅")
        await ctx.reply(embed=embed)
            
    @commands.command()
    async def ai_image(self, ctx, *query):
        """ -StrawBot returns an AI image"""
        author = ctx.author[:-2]
        init_string = ""
        string = ""
      
        for i in range(len(query)):
            if i == len(query) - 1:
                string += f"{query[i]}"
            else:
                string += f"{query[i]} "
        try:
            await ctx.message.add_reaction("<a:loading:1159345309172912178>")

            response = client.images.generate(
                model="dall-e-3",
                prompt= init_string + string,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            embed = discord.Embed(title="StrawBot AI Image", description=f"Generated image based on prompt: {string}", color=0x8717d7)
            embed.set_image(url=image_url)
            
            await ctx.message.add_reaction("✅")
            await ctx.reply(embed=embed)
            
        except Exception as e:
            await ctx.message.add_reaction("❌")
            print(e)
