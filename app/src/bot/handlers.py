# handlers.py

import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from ..models.drugs import Drugs, DrugTypes, DrugDosages, DosageForms
from ..services.crud_operations import (
    create_object,
    update_object,
    delete_object,
    get_object_by,
    list_objects,
)
from sqlalchemy.future import select

# Conversation states
CHOOSING, ADDING_DRUG_NAME, ADDING_DRUG_TYPE, ADDING_EXPIRY_DATE = range(4)

async def handle_start(update: Update, context: CallbackContext):
    keyboard = [['Аптечка', 'Комуналка']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)
    return CHOOSING

async def handle_choice(update: Update, context: CallbackContext):
    user_choice = update.message.text  
    
    if user_choice == 'Аптечка':
        await handle_aptechka(update, context)
        return CHOOSING
    elif user_choice == 'Комуналка':
        await update.message.reply_text('You chose Комуналка! Handling it now...')
        # await handle_komunalka(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text('Unknown option. Please choose Аптечка or Комуналка.')
        return CHOOSING

async def handle_aptechka(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Add Drug", callback_data='add_drug'),
            InlineKeyboardButton("Remove Drug", callback_data='remove_drug'),
        ],
        [
            InlineKeyboardButton("List Drugs", callback_data='list_drugs'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Please choose an action:', reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text('Please choose an action:', reply_markup=reply_markup)
    return CHOOSING

async def aptechka_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == 'add_drug':
        await query.edit_message_text('You chose to add a drug. Please enter the drug name:')
        return ADDING_DRUG_NAME
    elif choice == 'remove_drug':
        # Get list of drugs
        drugs = await list_objects(Drugs)
        if not drugs:
            await query.edit_message_text('Your medicine box is empty.')
            return ConversationHandler.END
        else:
            keyboard = []
            for drug in drugs:
                keyboard.append([InlineKeyboardButton(f"{drug.DrugName}", callback_data=f"remove_{drug.DrugID}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Select a drug to remove:', reply_markup=reply_markup)
            return CHOOSING
    elif choice == 'list_drugs':
        drugs = await list_objects(Drugs)
        if not drugs:
            await query.edit_message_text('Your medicine box is empty.')
        else:
            drugs_list = '\n'.join([f"{drug.DrugID}: {drug.DrugName} (Expires on {drug.ExpiryDate.strftime('%Y-%m-%d')})" for drug in drugs])
            await query.edit_message_text(f'Current drugs in your medicine box:\n{drugs_list}')
        return ConversationHandler.END
    elif choice.startswith('remove_'):
        drug_id = int(choice.split('_')[1])
        await delete_object(Drugs, drug_id)
        await query.edit_message_text('Drug removed successfully.')
        return ConversationHandler.END
    else:
        await query.edit_message_text('Unknown choice.')
        return ConversationHandler.END

async def add_drug_name(update: Update, context: CallbackContext):
    drug_name = update.message.text
    context.user_data['drug_name'] = drug_name

    # Now ask for the drug type
    await update.message.reply_text('Please enter the drug type:')
    return ADDING_DRUG_TYPE

async def add_drug_type(update: Update, context: CallbackContext):
    drug_type = update.message.text
    context.user_data['drug_type'] = drug_type

    await update.message.reply_text('Please enter the expiry date (YYYY-MM-DD):')
    return ADDING_EXPIRY_DATE

async def add_drug_expiry_date(update: Update, context: CallbackContext):
    expiry_date_str = update.message.text
    try:
        expiry_date = datetime.datetime.strptime(expiry_date_str, '%Y-%m-%d')
    except ValueError:
        await update.message.reply_text('Invalid date format. Please enter the date in YYYY-MM-DD format:')
        return ADDING_EXPIRY_DATE

    # Now we have all the data, create the drug entry
    drug_name = context.user_data['drug_name']
    drug_type_name = context.user_data['drug_type']

    # First, check if the drug type exists
    existing_drug_type = await get_object_by(DrugTypes, TypeName=drug_type_name)
    if existing_drug_type:
        drug_type_id = existing_drug_type.DrugTypeID
    else:
        # Create new drug type
        new_drug_type = await create_object(DrugTypes, TypeName=drug_type_name)
        drug_type_id = new_drug_type.DrugTypeID

    # Now create the drug
    new_drug = await create_object(Drugs, DrugName=drug_name, DrugTypeID=drug_type_id, ExpiryDate=expiry_date)

    await update.message.reply_text(f'Drug "{drug_name}" added successfully.')
    return ConversationHandler.END


def setup_bot(TOKEN):
    application = ApplicationBuilder().token(TOKEN).build()

    main_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handle_start)],
        states={
            CHOOSING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice),
                CallbackQueryHandler(aptechka_callback_handler),
            ],
            ADDING_DRUG_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_drug_name),
            ],
            ADDING_DRUG_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_drug_type),
            ],
            ADDING_EXPIRY_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_drug_expiry_date),
            ],
        },
        fallbacks=[],
    )

    application.add_handler(main_conv_handler)
    return application


if __name__ == '__main__':
    main()
