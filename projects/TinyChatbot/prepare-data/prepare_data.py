import json
from datasets import load_dataset

# ----------- CONFIGURATION -----------
dataset_name = "bkai-foundation-models/vi-alpaca"
output_filename = "vi-alpaca-500.jsonl"
num_samples = 500
# -------------------------------------

def prepare_dataset():
	print(f"Đang tải dataset '{dataset_name}' từ Hugging Face...")
	dataset = load_dataset(dataset_name, split="train", streaming=True)
	print(f"Đã tải thành công! Lấy {num_samples} mẫu đầu tiên để xử lý.")

	subset = dataset.take(num_samples)
	print(f"Đang chuyển đổi và lưu vào file '{output_filename}'...")
	with open(output_filename, 'w', encoding='utf-8') as outfile:
		count = 0
		for entry in subset:
			json.dump(entry, outfile, ensure_ascii=False)
			outfile.write('\n')
			count += 1

	print(f"--- HOÀN THÀNH ---")
	print(f"Đã xử lý và lưu thành công {count} mẫu vào file '{output_filename}'.")
	print("File này đã sẵn sàng để sử dụng cho việc fine-tuning.")

if __name__ == "__main__":
	prepare_dataset()
