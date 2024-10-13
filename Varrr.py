import discord
from discord.ext import commands

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
role_income = {}  # Хранилище дохода от ролей
role_cooldowns = {}  # Хранилище кулдаунов для ролей
shop_items = {}  # Добавляем инициализацию магазина
currency_symbol = "💵"  # Начальный символ валюты

### Команды ###

@bot.tree.command(name="role_income_add", description="Установить доход от роли")
async def role_income_add(interaction: discord.Interaction, role: discord.Role, amount: int, cooldown: int):
    role_income[role.id] = amount
    role_cooldowns[role.id] = cooldown * 3600  # Кулдаун в секундах (часы * 3600)
    embed = discord.Embed(
        title="✅ Доход от роли установлен!",
        description=f"Роль **{role.name}** теперь дает **{amount}** монет с кулдауном в **{cooldown} часов**.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="role_income_info", description="Показать информацию о доходах от ролей")
async def role_income_info(interaction: discord.Interaction):
    if not role_income:
        await interaction.response.send_message("❌ Нет зарегистрированных ролей с доходом.")
        return

    embed_description = "Список ролей и их доходов:\n"
    for role_id, amount in role_income.items():
        role = interaction.guild.get_role(role_id)
        if role:
            embed_description += f"**{role.name}**: **{amount}** монет\n"

    embed = discord.Embed(
        title="📊 Информация о доходах от ролей",
        description=embed_description,
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="collect", description="Собрать деньги (с кулдауном)")
@commands.cooldown(1, 60, commands.BucketType.user)
async def collect(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0  # Инициализируем баланс, если его нет

    total_earnings = 0  # Переменная для хранения общей суммы дохода
    embed_description = ""  # Строка для накопления описания доходов
    can_collect = False  # Флаг, указывающий, можно ли собрать деньги

    for role in interaction.user.roles:
        if role.id in role_income:
            # Проверяем кулдаун для данной роли
            last_collected = role_cooldowns.get(role.id, 0)
            if last_collected < (discord.utils.utcnow().timestamp() - role_cooldowns[role.id]):  # Проверка кулдауна
                earnings = role_income[role.id]
                total_earnings += earnings
                embed_description += f"Роль: **{role.name}** - Сумма: **{earnings}** монет\n"
                can_collect = True  # Можно собрать деньги
                # Обновляем время последнего сбора для этой роли
                role_cooldowns[role.id] = discord.utils.utcnow().timestamp()

    if total_earnings > 0:
        user_balances[user_id] += total_earnings  # Добавляем общую сумму к балансу пользователя
        embed = discord.Embed(
            title="💰 Сбор средств",
            description=embed_description,  # Теперь показывает все доходы
            color=discord.Color.green()
        )
        embed.add_field(name="Ваш текущий баланс:", value=f"{user_balances[user_id]} монет", inline=False)
        await interaction.response.send_message(embed=embed)
    elif not can_collect:
        # Если нет ролей с доходом или все они на кулдаун
        await interaction.response.send_message("❌ У вас нет ролей, которые дают доход, или кулдаун еще не истек для всех ролей.")
    else:
        await interaction.response.send_message("❌ Кулдаун для одной или нескольких ваших ролей еще не истек.")

#баланс
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

#кулдаун
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

bot.run('Token')