from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = '7606761993:AAFvACZ3C0Q4KSjcynsSjy8C1z7fuQfso6Q'  # 여기에 BotFather에서 받은 API 토큰 입력


async def start(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup([['자연광', '하얀 조명', '노란 조명', '어두운 실내']], one_time_keyboard=True)
    await update.message.reply_text("안녕하세요! 발색 사진을 보내주시면, 톤을 분석해 드릴게요. 환경을 선택해주세요.", reply_markup=reply_markup)

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    
    # 사용자가 선택한 환경을 받으면 사진을 기다리도록 안내
    if text in ['자연광', '하얀 조명', '노란 조명', '어두운 실내']:
        context.user_data['lighting'] = text
        await update.message.reply_text("사진을 보내주세요!")
    
    # 사진을 받으면 톤 분석 시작
    elif update.message.photo:
        file = update.message.photo[-1].get_file()
        file.download('user_image.jpg')  # 사진 저장
        lighting = context.user_data.get('lighting', '자연광')
        
        # 톤 분석 함수 호출 (여기서는 이미 작성한 톤 분석 코드 활용)
        tone = analyze_tone('user_image.jpg', lighting)  # 'analyze_tone'은 기존의 코드로 대체
        await update.message.reply_text(f"사진 분석 결과: '{tone}' 톤이에요! 🎨")
    else:
        await update.message.reply_text("발색 사진을 보내주세요.")

async def analyze_tone(image_path, lighting):
    # 여기서 기존 코드의 톤 분석 로직을 처리
    return "봄 웜"  # 예시로 봄 웜 톤을 반환합니다.

def main():
    # Application 클래스 사용
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))  # 사진 메시지 처리
    
    # polling 시작
    application.run_polling()

if __name__ == '__main__':
    main()
