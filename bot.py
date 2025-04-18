import logging
from telegram import Update, ForceReply
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackContext
)
from llm_handler import LLMHandler
from config import config
import asyncio

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class AITelegramBot:
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.user_conversations = {}  # Stores conversation history per user

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! I'm an AI assistant powered by {config.LLM_TYPE.upper()}. How can I help you today?",
            reply_markup=ForceReply(selective=True),
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        help_text = """
        🤖 AI Assistant Bot Help:

        Just send me a message and I'll respond using {llm_type}!

        Commands:
        /start - Start interacting with the bot
        /help - Show this help message
        /new - Start a new conversation (clear history)
        """.format(llm_type=config.LLM_TYPE.upper())
        await update.message.reply_text(help_text)

    async def new_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clear conversation history."""
        user_id = update.message.from_user.id
        self.user_conversations[user_id] = []
        await update.message.reply_text("Started a new conversation. Your previous messages have been forgotten.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages and generate responses."""
        user_id = update.message.from_user.id
        user_message = update.message.text

        # Initialize conversation history if needed
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []

        # Add user message to history
        self.user_conversations[user_id].append({"role": "user", "content": user_message})

        # Keep only the last MAX_HISTORY messages
        if len(self.user_conversations[user_id]) > config.MAX_HISTORY:
            self.user_conversations[user_id] = self.user_conversations[user_id][-config.MAX_HISTORY:]

        # Show typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # Get response from LLM
        response = await self.llm_handler.generate_response(self.user_conversations[user_id])

        # Add assistant response to history
        self.user_conversations[user_id].append({"role": "assistant", "content": response})

        # Send response (split if too long)
        if len(response) > config.MAX_MESSAGE_LENGTH:
            for x in range(0, len(response), config.MAX_MESSAGE_LENGTH):
                await update.message.reply_text(response[x:x + config.MAX_MESSAGE_LENGTH])
        else:
            await update.message.reply_text(response)

    async def error_handler(self, update: object, context: CallbackContext) -> None:
        """Log errors and send a message to the user."""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        if update and hasattr(update, 'message'):
            await update.message.reply_text("Sorry, I encountered an error processing your message. Please try again.")

    async def shutdown(self, application: Application) -> None:
        """Cleanup tasks before shutdown."""
        await self.llm_handler.close()

    def run(self):
        """Start the bot."""
        # Create the Application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("new", self.new_conversation))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Add error handler
        application.add_error_handler(self.error_handler)

        # Add shutdown handler
        application.post_shutdown(self.shutdown)

        # Run the bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = AITelegramBot()
    bot.run()
