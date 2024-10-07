import discord
from discord.ext import commands

# Создаем объект бота с интентами
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Команды бота синхронизированы.")

    async def on_ready(self):
        print(f'Бот {self.user} запущен и готов!')

bot = MyBot()

# Хранилище данных о фракциях, странах, альянсах, войнах, технологиях и территориях
factions = {}
countries = {}
alliances = {}
wars = {}
technologies = {}
territories = {}
armies = {}
spies = {}
ranks = ['Генерал', 'Министр', 'Советник', 'Офицер']

### Фракции ###

@bot.tree.command(name="faction_info", description="Показать информацию о фракции")
async def faction_info(interaction: discord.Interaction, faction: str):
    if faction not in factions:
        await interaction.response.send_message(f"❌ Фракция `{faction}` не найдена.")
    else:
        leader = factions[faction]["leader"]
        resources = factions[faction]["resources"]
        embed = discord.Embed(
            title=f"📜 Информация о фракции: {faction}",
            color=discord.Color.purple()
        )
        embed.add_field(name="👑 Лидер", value=leader, inline=False)
        embed.add_field(name="💰 Ресурсы", value=f"{resources}", inline=False)
        embed.set_footer(text="Информация о фракции", icon_url="https://example.com/icon.png")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="list_factions", description="Показать список всех фракций")
async def list_factions(interaction: discord.Interaction):
    if not factions:
        await interaction.response.send_message("📜 Список фракций пуст.")
    else:
        factions_list = "\n".join([f"🔹 {name}" for name in factions.keys()])
        embed = discord.Embed(
            title="🌍 Список фракций",
            description=factions_list,
            color=discord.Color.green()
        )
        embed.set_footer(text="Выберите фракцию для подробной информации")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="create_faction", description="Создать новую фракцию")
async def create_faction(interaction: discord.Interaction, faction: str, leader: str, resources: int):
    if faction in factions:
        await interaction.response.send_message(f"⚠️ Фракция {faction} уже существует.")
    else:
        factions[faction] = {"leader": leader, "resources": resources}
        embed = discord.Embed(
            title="✅ Фракция создана!",
            color=discord.Color.blue()
        )
        embed.add_field(name="🏴 Фракция", value=faction, inline=False)
        embed.add_field(name="👑 Лидер", value=leader, inline=False)
        embed.add_field(name="💰 Ресурсы", value=resources, inline=False)
        embed.set_thumbnail(url="https://example.com/faction.png")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="delete_faction", description="Удалить фракцию")
async def delete_faction(interaction: discord.Interaction, faction: str):
    if faction not in factions:
        await interaction.response.send_message(f"❌ Фракция {faction} не найдена.")
    else:
        del factions[faction]
        embed = discord.Embed(
            title="🗑️ Фракция удалена",
            description=f"Фракция **{faction}** была удалена.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

### Страны ###

@bot.tree.command(name="register_country", description="Зарегистрировать новую страну за игроком")
async def register_country(interaction: discord.Interaction, player: discord.Member, country: str, ideology: discord.Role, iron: str, oil: str, uranium: str, coal: str):
    if country in countries:
        await interaction.response.send_message(f"⚠️ Страна {country} уже существует.")
        return

    # Регистрация страны
    countries[country] = {
        "player": player.name,
        "ideology": ideology,
        "resources": {
            "iron": iron,
            "oil": oil,
            "uranium": uranium,
            "coal": coal
        }
    }

    # Выдача ролей
    if iron.lower() == "yes":
        await player.add_roles(discord.utils.get(interaction.guild.roles, id=IRON_ROLE_ID))  # Замените на ID роли для железа
    if oil.lower() == "yes":
        await player.add_roles(discord.utils.get(interaction.guild.roles, id=OIL_ROLE_ID))  # Замените на ID роли для нефти
    if uranium.lower() == "yes":
        await player.add_roles(discord.utils.get(interaction.guild.roles, id=URANIUM_ROLE_ID))  # Замените на ID роли для урана
    if coal.lower() == "yes":
        await player.add_roles(discord.utils.get(interaction.guild.roles, id=COAL_ROLE_ID))  # Замените на ID роли для угля

    # Создание ответа
    embed = discord.Embed(
        title="🌟 Страна зарегистрирована!",
        color=discord.Color.green()
    )
    embed.add_field(name="🏳️ Страна", value=country, inline=False)
    embed.add_field(name="👤 Игрок", value=player.name, inline=True)
    embed.add_field(name="📜 Идеология", value=ideology.name, inline=True)
    embed.add_field(name="⛏️ Ресурсы", value=f"Железо: {iron}, Нефть: {oil}, Уран: {uranium}, Уголь: {coal}", inline=False)
    embed.set_thumbnail(url="https://example.com/country.png")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="list_countries", description="Показать список всех стран")
async def list_countries(interaction: discord.Interaction):
    if not countries:
        await interaction.response.send_message("📜 Список стран пуст.")
    else:
        countries_list = "\n".join([f"🌍 {name}" for name in countries.keys()])
        embed = discord.Embed(
            title="🌍 Список стран",
            description=countries_list,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Выберите страну для получения информации")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="delete_country", description="Удалить страну")
async def delete_country(interaction: discord.Interaction, country: str):
    if country not in countries:
        await interaction.response.send_message(f"❌ Страна {country} не найдена.")
    else:
        del countries[country]
        embed = discord.Embed(
            title="🗑️ Страна удалена",
            description=f"Страна **{country}** была удалена.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="collect_resources", description="Собрать ресурсы для страны")
async def collect_resources(interaction: discord.Interaction, country: str):
    if country not in countries:
        await interaction.response.send_message(f"❌ Страна {country} не найдена.")
    else:
        collected_resources = countries[country]["resources"]["iron"] + 100  # Пример начисления ресурсов
        countries[country]["resources"]["iron"] = collected_resources
        embed = discord.Embed(
            title="💰 Ресурсы собраны!",
            description=f"Ресурсы для страны **{country}** собраны. Новое количество ресурсов: **{collected_resources}**.",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

### Дипломатия и Альянсы ###

@bot.tree.command(name="create_alliance", description="Создать альянс между двумя странами")
async def create_alliance(interaction: discord.Interaction, country1: str, country2: str, name: str):
    if country1 not in countries or country2 not in countries:
        await interaction.response.send_message("❌ Одна из стран не найдена.")
    else:
        alliances[name] = [country1, country2]
        embed = discord.Embed(
            title="🤝 Альянс создан!",
            description=f"Альянс **{name}** создан между **{country1}** и **{country2}**.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Сила в единстве!")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="break_alliance", description="Разорвать альянс")
async def break_alliance(interaction: discord.Interaction, name: str):
    if name not in alliances:
        await interaction.response.send_message(f"❌ Альянс {name} не найден.")
    else:
        del alliances[name]
        embed = discord.Embed(
            title="✂️ Альянс разорван",
            description=f"Альянс **{name}** был разорван.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="war", description="Объявить войну одной или нескольким странам")
async def declare_war(interaction: discord.Interaction, countries_list: str):
    countries_to_war = countries_list.split(',')
    for country in countries_to_war:
        if country.strip() not in countries:
            await interaction.response.send_message(f"❌ Страна {country.strip()} не найдена.")
            return

    # Добавление стран в список войн
    wars[interaction.user.name] = countries_to_war
    embed = discord.Embed(
        title="⚔️ Объявление войны!",
        description=f"Объявлена война странам: {', '.join(countries_to_war)}.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

### Модераторские команды ###

@bot.tree.command(name="clear", description="Очистить сообщения в канале")
@commands.has_permissions(manage_messages=True)
async def clear_messages(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    embed = discord.Embed(
        title="🧹 Очистка завершена!",
        description=f"Удалено сообщений: {amount}.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="mute", description="Замьютить пользователя")
@commands.has_permissions(manage_roles=True)
async def mute_user(interaction: discord.Interaction, member: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name="Muted")  # Замените на имя вашей роли мьют
    await member.add_roles(role)
    embed = discord.Embed(
        title="🔇 Пользователь замучен!",
        description=f"{member.mention} был замучен.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="unmute", description="Размьютить пользователя")
@commands.has_permissions(manage_roles=True)
async def unmute_user(interaction: discord.Interaction, member: discord.Member):
    role = discord.utils.get(interaction.guild.roles, name="Muted")  # Замените на имя вашей роли мьют
    await member.remove_roles(role)
    embed = discord.Embed(
        title="🔊 Пользователь размучен!",
        description=f"{member.mention} был размучен.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)
