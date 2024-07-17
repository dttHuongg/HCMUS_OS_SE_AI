from logic import pl_resolution, read_file, write_file
import os

print('Enter test file ID (e.g., 01, 02, 03, ...):', end = ' ')
test_case = input().strip()
current_dir = os.getcwd()

input_file = os.path.join(current_dir, 'src', 'test', f'{test_case}.txt')
output_file = os.path.join(current_dir, 'src', 'test', f'{test_case}_out.txt')

# read file
kb, alpha = read_file(input_file)
print(f'Having already read from {input_file}')

entailment, steps = pl_resolution(kb, alpha)

# write file
write_file(output_file, steps, entailment)
print(f'Having already written output to {output_file}')
