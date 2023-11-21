
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
    def chat_gpt(message):
        messages = [ {"role": "system", "content":
                    "You are a Discord bot that acts as a cheeky and dry humored, but intelligent assistant named StrawBot that responds with concise answers."} ] 
        while True: 
            if message: 
                messages.append({"role": "user", "content": message},) 
                chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages) 
            reply = chat.choices[0].message.content 
            messages.append({"role": "assistant", "content": reply})
            return reply
        
    @commands.command()
    async def ai(self, ctx, *query):
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
        
        embed=discord.Embed(title="ScaryBot AI", description=reply, color=0x8717d7)
        await ctx.reply(embed=embed)
            
        await ctx.message.add_reaction("✅")
