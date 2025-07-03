import discord
from discord.ext import commands
import json
import os
import datetime
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Cargar token
load_dotenv()

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Crear bot
bot = commands.Bot(command_prefix="#$#", intents=intents)

# Diccionario de rangos por puntos
rangos = [
    (30000, "ﾟ✧ Pilar Eterno"),
    (20000, "✦❛₊ ⋆﹒Corazón del exilio"),
    (15000, "﹒♱﹒Sombra Iluminada！﹐◞"),
    (10000, "”﹒Serafín Roto﹒⊹ ﹒ ₊"),
    (5000, "୨୧﹒Portador del Umbral ﹒⌑˚﹒"),
    (2500, "🍙ノ﹒Consejero Estelar﹒ᰔ ୨"),
    (1000, "゛ ۶ৎ﹒Portador de Estrellas ﹒"),
    (500, "⊹ ﹒ ₊ Invocador ｡⋆🕸 ⟡﹕"),
    (200, "꒰🐑﹒Aurora Clara ﹒あ ᵎᵎ"),
    (50, "彡⌑﹒ Alma nueva  ﹒꒰ဣ꒱"),
]

# Cargar puntos desde archivo
def cargar_puntos():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

# Guardar puntos
def guardar_puntos(puntos):
    with open("data.json", "w") as f:
        json.dump(puntos, f)

puntos = cargar_puntos()

# Comando para resetear puntos
@bot.command()
async def resetpuntos(ctx):
    rol_autorizado = discord.utils.get(ctx.author.roles, name="꒰☆﹒staff ୨🍴")

    if rol_autorizado:
        global puntos
        puntos = {}  # Reinicia puntos
        guardar_puntos(puntos)

        roles_rango = [nombre for _, nombre in rangos]
        for member in ctx.guild.members:
            for rol in member.roles:
                if rol.name in roles_rango:
                    try:
                        await member.remove_roles(rol)
                    except:
                        pass  # Ignora errores por permisos

        await ctx.send("🧨 Todos los puntos han sido reiniciados y los rangos eliminados.")
    else:
        await ctx.send("🚫 No tienes permiso para usar este comando.")

@bot.command()
async def asistencia(ctx):
    user_id = str(ctx.author.id)
    today = datetime.datetime.now().date()
    member = ctx.author  # objeto Member para acceder a roles

    # Cargar datos
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Inicializar usuario si no existe
    if user_id not in data:
        data[user_id] = {
            "puntos": 0,
            "rango": "Sin rango",
            "ultima_asistencia": "",
            "racha": 0,
            "racha_mensual": 0
        }

    user = data[user_id]
    ultima_asistencia = user.get("ultima_asistencia")

    # Verificar si ya asistió hoy
    if ultima_asistencia == str(today):
        await ctx.send(f"⚠️ Ya registraste tu asistencia hoy, <@{ctx.author.id}>.")
        return

    # Actualizar racha diaria
    if ultima_asistencia == str(today - datetime.timedelta(days=1)):
        user["racha"] += 1
    else:
        user["racha"] = 1

    # Actualizar racha mensual
    if today.day == 1:
        user["racha_mensual"] = 1
    else:
        user["racha_mensual"] += 1

    user["ultima_asistencia"] = str(today)

    # Guardar cambios
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

    # Lista oficial de rangos para verificar roles
    lista_rangos = [
        "Alma Nueva", "Aurora Clara", "Invocador", "Portador de Estrellas",
        "Consejero Estelar", "Portador del Umbral", "Serafín Roto",
        "Sombra Iluminada", "Corazón del Exilio", "Pilar Eterno"
    ]

    # Extraer nombre de rango según rol que tenga el usuario (el primero que coincida)
    roles_usuario = [role.name for role in member.roles]
    rango_encontrado = next((r for r in lista_rangos if r in roles_usuario), "Sin rango")

    # Crear embed
    embed = discord.Embed(
        title="✅ Asistencia registrada",
        description=f"<@{ctx.author.id}> ha marcado asistencia correctamente.",
        color=discord.Color.green()
    )
    embed.add_field(name="📅 Fecha", value=str(today), inline=True)
    embed.add_field(name="🔥 Racha actual", value=f"{user['racha']} días", inline=True)
    embed.add_field(name="📆 Racha mensual", value=f"{user['racha_mensual']} días", inline=True)
    embed.add_field(name="🌟 Rango", value=rango_encontrado, inline=False)
    embed.set_footer(text="The Seraph's Heresy · Sistema de asistencia")

    await ctx.send(embed=embed)

@bot.command()
async def marcha(ctx):
    await ctx.message.delete()  # 🔥 Borra el mensaje que contiene !marcha

    mensaje = (
        "# ¡Hijos del Exilio, prepárense!\n"
        "La rebelión resuena entre las estrellas y **hoy martes** a las **7:00 PM (CDMX)** se alza la **Marcha del Serafín**.\n"
        "Afilen sus alas, ajusten sus rangos y reúnanse en **PonyTown** para hacer temblar los cielos.\n\n"
        "✨ Asistir suma **+50 puntos**\n"
        "🔥 Ganar juegos suma **+10 puntos**\n"
        "🌟 Las rachas cuentan… y **la gloria también**.\n\n"
        "🕊️ *Que el Dogma tiemble y la Luz sea libre.*\n\n"
        "> 🕖 Si estás en otro país, revisa la tabla horaria o pregunta sin pena.\n"
        "> 🎮 No olvides usar el comando `!asistencia` para registrar tu presencia."
    )

    await ctx.send(mensaje)

# Comando para ver puntos
@bot.command()
async def verpuntos(ctx, miembro: discord.Member = None):
    miembro = miembro or ctx.author
    id_usuario = str(miembro.id)
    total = puntos.get(id_usuario, 0)
    await ctx.send(f"📊 **{miembro.display_name}** tiene **{total}** puntos.")

# Comando para asignar puntos
@bot.command()
async def puntosadd(ctx, member: discord.Member, puntos_a_sumar: int):
    nombre_rol_autorizado = "꒰☆﹒staff ୨🍴"
    
    tiene_permiso = any(role.name == nombre_rol_autorizado for role in ctx.author.roles)
    if not tiene_permiso:
        await ctx.send("🚫 No tienes permiso para usar este comando.")
        return

    user_id = str(member.id)
    puntos[user_id] = puntos.get(user_id, 0) + puntos_a_sumar
    guardar_puntos(puntos)
    nuevo_total = puntos[user_id]

    await ctx.send(f"✅ Se han agregado {puntos_a_sumar} puntos a {member.display_name}. Total ahora: {nuevo_total} puntos.")

    # Quitar otros rangos
    roles_servidor = [r for _, r in rangos]
    for rol in member.roles:
        if rol.name in roles_servidor:
            await member.remove_roles(rol)

    # Asignar nuevo rango
    nuevo_rango = None
    for puntos_necesarios, nombre_rango in sorted(rangos, reverse=True):
        if nuevo_total >= puntos_necesarios:
            nuevo_rango = nombre_rango
            break

    if nuevo_rango:
        rol = discord.utils.get(ctx.guild.roles, name=nuevo_rango)
        if rol:
            await member.add_roles(rol)
            await ctx.send(f"✅ {member.mention} ahora es **{nuevo_rango}** con **{nuevo_total}** puntos.")
        else:
            await ctx.send(f"⚠️ El rol **{nuevo_rango}** no existe en este servidor.")
    else:
        await ctx.send(f"✅ {member.mention} recibió **{puntos_a_sumar}** puntos. Total: **{nuevo_total}**")

# Evento al iniciar
@bot.event
async def on_ready():
    print(f"🔮 Bot conectado como {bot.user}")

# Servidor web para evitar que Render lo duerma
app = Flask('')

@app.route('/')
def home():
    return "Bot activo"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# Ejecutar bot
bot.run(os.getenv("TOKEN")) #--------
