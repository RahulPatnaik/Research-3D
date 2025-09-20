import os
import time

import transformers
from transformers import HfArgumentParser

from brickgpt.models import BrickGPT, BrickGPTConfig
from brickgpt.render_bricks import render_bricks


def main():
    parser = HfArgumentParser(BrickGPTConfig)
    (cfg,) = parser.parse_args_into_dataclasses()

    brickgpt = BrickGPT(cfg)
    prompt = input('Enter a prompt, or <Return> to exit: ')

    while True:
        if not prompt:
            break

        # Take user input
        filename = input('Enter a filename to save the output image (default=output.png): ')
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(filename)[0] if filename else 'output'
        txt_filename = os.path.abspath(base_name + '.txt')
        ldr_filename = os.path.abspath(base_name + '.ldr')
        img_filename = os.path.abspath(base_name + '.png')

        seed = input('Enter a generation seed (default=42): ')
        seed = int(seed) if seed else 42
        transformers.set_seed(seed)

        # Generate bricks
        print('Generating...')
        start_time = time.time()
        output = brickgpt(prompt)
        end_time = time.time()

        # Save results
        with open(txt_filename, 'w') as f:
            f.write(output['bricks'].to_txt())
        with open(ldr_filename, 'w') as f:
            f.write(output['bricks'].to_ldr())
        render_bricks(ldr_filename, img_filename)

        # Print results
        print('--------------------')
        print(f'Finished generating in {end_time - start_time:.2f}s.')
        print('Total # bricks:', len(output['bricks']))
        print('Total # brick rejections:', output['rejection_reasons'].total())
        print('Brick rejection reasons:', dict(output['rejection_reasons']))
        print('Total # regenerations:', output['n_regenerations'])
        print(f'Saved results to {txt_filename}, {ldr_filename}, and {img_filename}')
        print('--------------------')

        prompt = input('Enter another prompt, or <Return> to exit: ')


if __name__ == '__main__':
    main()
