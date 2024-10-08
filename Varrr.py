import discord
import os
from discord.ext import commands

#токен
TOKEN = os.getenv("DISCORD_TOKEN")

# Создаем объект бота с интентами
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="*", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Команды бота синхронизированы.")

    async def on_ready(self):
        print(f'Бот {self.user} запущен и готов!')

bot = MyBot()

# Хранилище данных
user_balances = {}
shop_items = {
    "Меч": 100,
    "Щит": 150,
    "Зелье": 50
}
user_inventories = {}  # Хранилище инвентарей пользователей
COOLDOWN_TIME = 60  # Время кулдауна для команды collect
currency_symbol = "💵"  # Начальный символ валюты

### Команды ###

@bot.tree.command(name="collect", description="Собрать деньги (с кулдауном)")
@commands.cooldown(1, COOLDOWN_TIME, commands.BucketType.user)
async def collect(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    earnings = 100  # Сумма, которую игрок получает при сборе
    user_balances[user_id] += earnings

    embed = discord.Embed(
        title="💰 Сбор средств",
        description=f"Вы собрали {earnings} монет!",
        color=discord.Color.green()
    )
    embed.add_field(name="Ваш текущий баланс:", value=f"{user_balances[user_id]} монет", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="balance", description="Показать баланс игрока")
async def balance(interaction: discord.Interaction):
    user_id = interaction.user.id
    balance = user_balances.get(user_id, 0)

    embed = discord.Embed(
        title="📊 Ваш баланс",
        description=f"Ваш текущий баланс: {balance} {currency_symbol}.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="shop", description="Показать товары в магазине")
async def shop(interaction: discord.Interaction):
    if not shop_items:
        await interaction.response.send_message("🛒 Магазин пуст.")
        return

    shop_list = "\n".join([f"**{item}**: {price} {currency_symbol}" for item, price in shop_items.items()])
    embed = discord.Embed(
        title="🛒 Магазин",
        description=shop_list,
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

# Команда инвентаря
@bot.tree.command(name="inventory", description="Показать инвентарь игрока")
async def inventory(interaction: discord.Interaction):
    user_id = interaction.user.id

    # Получаем инвентарь пользователя
    inventory = user_inventories.get(user_id, {})

    if not inventory:
        await interaction.response.send_message("🗃️ Ваш инвентарь пуст.")
        return

    # Формируем строку с количеством предметов
    inventory_list = "\n".join([f"{count} - {item}" for item, count in inventory.items()])

    embed = discord.Embed(
        title="🗃️ Ваш инвентарь",
        description=inventory_list,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# Создать предмет
@bot.tree.command(name="create_item", description="Создать новый предмет")
async def create_item(interaction: discord.Interaction, name: str, price: int, description: str):
    # Создаем новый предмет в магазине
    shop_items[name] = price

    # Выводим сообщение о успешном создании
    embed = discord.Embed(
        title="✅ Предмет создан!",
        description=f"Вы создали предмет **{name}** за **{price} монет**.\nОписание: {description}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# Удалить предмет
@bot.tree.command(name="delete_item", description="Удалить предмет из магазина")
async def delete_item(interaction: discord.Interaction, item: str):
    # Проверяем, есть ли предмет в магазине
    if item not in shop_items:
        await interaction.response.send_message(f"❌ Товар `{item}` не найден в магазине.")
        return

    # Удаляем предмет из магазина
    del shop_items[item]

    embed = discord.Embed(
        title="🗑️ Удаление товара",
        description=f"Предмет `{item}` был удален из магазина.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

# Изменение валюты
@bot.tree.command(name="set_currency", description="Изменить символ валюты")
async def set_currency(interaction: discord.Interaction, symbol: str):
    global currency_symbol
    currency_symbol = symbol
    embed = discord.Embed(
        title="💰 Символ валюты изменен!",
        description=f"Новый символ валюты: {currency_symbol}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# Новая команда для покупки товаров
@bot.tree.command(name="buy", description="Купить товар в магазине")
async def buy(interaction: discord.Interaction, item: str, quantity: int = 1):
    user_id = interaction.user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    if item not in shop_items:
        await interaction.response.send_message(f"❌ Товар `{item}` не найден в магазине.")
        return

    price = shop_items[item]  # Получаем цену товара
    total_cost = price * quantity

    if user_balances[user_id] < total_cost:
        await interaction.response.send_message(f"❌ У вас недостаточно денег для покупки {quantity} единиц товара `{item}`.")
        return

    # Списываем деньги
    user_balances[user_id] -= total_cost

    # Добавляем товар в инвентарь пользователя
    if user_id not in user_inventories:
        user_inventories[user_id] = {}
    
    if item in user_inventories[user_id]:
        user_inventories[user_id][item] += quantity  # Увеличиваем количество
    else:
        user_inventories[user_id][item] = quantity  # Добавляем новый предмет

    embed = discord.Embed(
        title="✅ Покупка успешна!",
        description=f"Вы купили {quantity} единиц товара `{item}` за {total_cost} {currency_symbol}.",
        color=discord.Color.green()
    )
    embed.add_field(name="Ваш текущий баланс:", value=f"{user_balances[user_id]} {currency_symbol}", inline=False)
    await interaction.response.send_message(embed=embed)

# Использовать предмет
@bot.tree.command(name="use_item", description="Использовать предмет из инвентаря")
async def use_item(interaction: discord.Interaction, item: str, quantity: int = 1):
    user_id = interaction.user.id

    if user_id not in user_inventories or item not in user_inventories[user_id]:
        await interaction.response.send_message(f"❌ У вас нет предмета `{item}` в инвентаре.")
        return

    # Подсчитаем, сколько предметов у пользователя
    item_count = user_inventories[user_id].get(item, 0)

    if item_count < quantity:
        await interaction.response.send_message(f"❌ У вас недостаточно предметов `{item}` для использования {quantity} раз.")
        return

    # Убираем нужное количество предметов из инвентаря
    user_inventories[user_id][item] -= quantity
    if user_inventories[user_id][item] == 0:
        del user_inventories[user_id][item]  # Удаляем предмет, если количество стало 0

    embed = discord.Embed(
        title="✅ Использование предмета",
        description=f"Вы использовали {quantity} предметов `{item}`.",
        color=discord.Color.green()
    )
    embed.add_field(name="Ваш инвентарь", value=", ".join([f"{count} - {name}" for name, count in user_inventories[user_id].items()]) or "Пусто", inline=False)
    await interaction.response.send_message(embed=embed)

# Остальные команды

@bot.tree.command(name="sell_item", description="Продать товар из инвентаря")
async def sell_item(interaction: discord.Interaction, item: str):
    user_id = interaction.user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    if user_id not in user_inventories or item not in user_inventories[user_id]:
        await interaction.response.send_message(f"❌ У вас нет товара `{item}` для продажи.")
        return

    price = shop_items.get(item, 50)  # Продаем по половине или фиксированной цене
    user_balances[user_id] += price
    user_inventories[user_id].remove(item)

    embed = discord.Embed(
        title="✅ Продажа успешна!",
        description=f"Вы продали `{item}` за {price} монет.",
        color=discord.Color.green()
    )
    embed.add_field(name="Ваш текущий баланс:", value=f"{user_balances[user_id]} монет", inline=False)
    embed.add_field(name="Ваш инвентарь", value=", ".join(user_inventories[user_id]) or "Пусто", inline=False)
    await interaction.response.send_message(embed=embed)

# Добавляем деньги любому игроку
@bot.tree.command(name="add_money", description="Добавить деньги игроку")
async def add_money(interaction: discord.Interaction, player: discord.Member, amount: int):
    user_id = player.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    user_balances[user_id] += amount
    embed = discord.Embed(
        title="✅ Деньги добавлены!",
        description=f"Вы добавили {amount} монет игроку {player.mention}.",
        color=discord.Color.green()
    )
    embed.add_field(name="Текущий баланс игрока", value=f"{user_balances[user_id]} монет", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove_money", description="Удалить деньги у игрока")
async def remove_money(interaction: discord.Interaction, amount: int):
    user_id = interaction.user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    if user_balances[user_id] < amount:
        await interaction.response.send_message("❌ У вас недостаточно денег для удаления этой суммы.")
        return

    user_balances[user_id] -= amount
    embed = discord.Embed(
        title="✅ Деньги удалены!",
        description=f"Вы удалили {amount} монет. Ваш текущий баланс: {user_balances[user_id]} монет.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="Показать рейтинг игроков")
async def leaderboard(interaction: discord.Interaction):
    sorted_balances = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)
    leaderboard_list = "\n".join([f"<@{user_id}>: {balance} монет" for user_id, balance in sorted_balances])
    embed = discord.Embed(
        title="🏆 Рейтинг игроков",
        description=leaderboard_list or "Пока нет игроков.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset_money", description="Сбросить деньги игрока")
async def reset_money(interaction: discord.Interaction, player: discord.Member):
    user_id = player.id
    user_balances[user_id] = 0
    embed = discord.Embed(
        title="✅ Деньги сброшены!",
        description=f"Деньги игрока <@{user_id}> были сброшены.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)
#бан
@bot.tree.command(name="ban", description="Забанить пользователя")
@commands.has_permissions(ban_members=True)  # Убедитесь, что у вызывающего команду есть права на бан
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "Причина не указана"):
    try:
        await user.ban(reason=reason)
        embed = discord.Embed(
            title="🚫 Пользователь забанен",
            description=f"Пользователь {user.mention} был забанен.\nПричина: {reason}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ У меня нет прав на бан этого пользователя.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)

# разбан
@bot.tree.command(name="unban", description="Разбанить пользователя")
@commands.has_permissions(ban_members=True)  # Убедитесь, что у вызывающего команду есть права на разбан
async def unban(interaction: discord.Interaction, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        embed = discord.Embed(
            title="✅ Пользователь разбанен",
            description=f"Пользователь {user.mention} был разбанен.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except discord.NotFound:
        await interaction.response.send_message("❌ Пользователь с таким ID не найден или не забанен.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)

#мьют и размьют
@bot.tree.command(name="mute", description="Мьютит пользователя на определенное время")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int):
    try:
        # Мьютим пользователя
        await member.timeout(duration=discord.utils.utcnow() + discord.timedelta(seconds=duration))
        embed = discord.Embed(
            title="🔇 Мьют",
            description=f"{member.mention} был замьючен на {duration} секунд.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Не удалось замьютить пользователя. Ошибка: {e}")

@bot.tree.command(name="unmute", description="Размьютит пользователя")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        # Размьютим пользователя
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Размьют",
            description=f"{member.mention} был размьючен.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Не удалось размьютить пользователя. Ошибка: {e}")

#деньги роль
@bot.tree.command(name="role_income", description="Установить доход от роли")
async def role_income(interaction: discord.Interaction, role: discord.Role, amount: int):
    for member in role.members:
        if member.id not in user_balances:
            user_balances[member.id] = 0  # Инициализируем баланс, если его нет
        user_balances[member.id] += amount

    embed = discord.Embed(
        title="✅ Доход добавлен!",
        description=f"Доход в размере {amount} монет был добавлен всем участникам роли `{role.name}`.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="set_cooldown", description="Установить кулдаун для команды collect")
async def set_cooldown(interaction: discord.Interaction, seconds: int):
    global COOLDOWN_TIME
    COOLDOWN_TIME = seconds
    embed = discord.Embed(
        title="⏳ Кулдаун установлен!",
        description=f"Кулдаун для команды collect установлен на {seconds} секунд.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)


#запуск
bot.run(TOKEN)
