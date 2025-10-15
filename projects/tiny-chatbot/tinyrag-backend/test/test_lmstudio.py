import openai

try:
	client = openai.OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
except openai.OpenAIError as e:
	print(f"Lỗi khi khởi tạo OpenAI client: {e}")
	client = None


MODELS_TO_TEST = [
	"meta-llama-3.1-8b-instruct",
	"openai/gpt-oss-20b",
	"phi-3-mini-128k-instruct-imatrix-smashed"
]


# --- HÀM KIỂM TRA ---

def test_model(model_name: str):
	if not client:
		print("Client chưa được khởi tạo, bỏ qua kiểm tra.")
		return

	print("-" * 50)
	print(f"▶️  Đang gửi yêu cầu đến model: {model_name}...")

	try:
		completion = client.chat.completions.create(
			model=model_name,
			messages=[
				{"role": "system", "content": "Bạn là một trợ lý AI hữu ích, luôn trả lời bằng tiếng Việt."},
				{"role": "user", "content": "Hãy giải thích ngắn gọn về khái niệm 'API'."}
			],
			temperature=0.7,
			timeout=60  # Đặt thời gian chờ là 60 giây
		)

		response = completion.choices[0].message.content
		print(f"✅ --- Phản hồi từ AI ---")
		print(response)

	except openai.NotFoundError:
		print(f"❌ LỖI: Model '{model_name}' không được tìm thấy trên server.")
		print("   Hãy kiểm tra xem bạn đã load đúng model trong LM Studio chưa.")
	except openai.APIConnectionError:
		print("❌ LỖI KẾT NỐI: Không thể kết nối đến LM Studio Server tại http://localhost:1234.")
		print("   Hãy đảm bảo LM Studio Server đang chạy.")
		return False  # Trả về False để dừng vòng lặp
	except Exception as e:
		print(f"❌ Đã có một lỗi không xác định xảy ra với model '{model_name}': {e}")

	print("-" * 50 + "\n")
	return True

if __name__ == "__main__":
	print("Bắt đầu kiểm tra các model trên LM Studio Server...\n")
	if client:
		for model in MODELS_TO_TEST:
			if not test_model(model):
				break
	else:
		print("Không thể thực hiện kiểm tra do lỗi khởi tạo client.")

	print("Hoàn tất kiểm tra.")
