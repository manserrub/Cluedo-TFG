# 🔍 CLUEDO - Trabajo de Fin de Grado

Una aplicación interactiva basada en el clásico juego de Cluedo, desarrollada con **Streamlit** y potenciada con inteligencia artificial.

## 🚀 Descripción

CLUEDO es una versión digital del juego de mesa tradicional donde debes resolver un misterio identificando al culpable, el arma utilizada y la ubicación del crimen. La aplicación utiliza tecnología de IA para generar dinámicamente pistas y gestionar la lógica del juego.

## 📱 Aplicación Desplegada

La aplicación está disponible en vivo en:
**[https://cluedo-manserrub.streamlit.app/](https://cluedo-manserrub.streamlit.app/)**

## 💻 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/manserrub/Cluedo-TFG.git
cd Cluedo-TFG
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 🎮 Uso

Para ejecutar la aplicación localmente:

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador por defecto en `http://localhost:8501`

## 📦 Dependencias

- **streamlit** (>=1.25.0): Framework para crear la aplicación web
- **psycopg2-binary** (>=2.9.10): Adaptador PostgreSQL para Python
- **openai** (>=1.0.0): API de OpenAI para inteligencia artificial
- **bcrypt** (>=4.0.0): Librería para encriptación de contraseñas

## 📁 Estructura del Proyecto

```
Cluedo-TFG/
├── app.py                 # Punto de entrada principal
├── requirements.txt       # Dependencias del proyecto
├── README.md             # Este archivo
├── logic/                # Módulos de lógica del juego
│   └── estilos.py       # Configuración de estilos
├── pantallas/           # Módulos de interfaz de usuario
│   ├── inicio.py        # Pantalla de inicio
│   ├── seleccion.py     # Pantalla de selección
│   └── juego.py         # Pantalla del juego
└── assets/              # Recursos estáticos (imágenes, etc.)
```

## 🎯 Características

- ✨ Interfaz intuitiva y atractiva
- 🤖 Integración con IA para generar pistas dinámicas
- 🔐 Autenticación segura de usuarios
- 💾 Persistencia de datos en base de datos PostgreSQL
- 📱 Diseño responsive adaptado a dispositivos

## 👨‍💻 Autor

- **Manserrub** - [GitHub](https://github.com/manserrub)

## 📝 Licencia

Este proyecto está disponible bajo licencia MIT. Consulta el archivo LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes, abre un issue primero para discutir qué te gustaría cambiar.

## 📞 Soporte

Si encuentras problemas o tienes sugerencias, abre un [issue](https://github.com/manserrub/Cluedo-TFG/issues) en el repositorio.

---

**Última actualización**: 2026
