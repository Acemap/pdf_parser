import argparse
from .parser import Parser

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('-b', '--backend', default='grobid', help='Backend to use. (Default: grobid)')
    arg_parser.add_argument('-t', '--type', default='text', help='Type of content. (Default: text)')
    arg_parser.add_argument('-n', '--thread', default=0, help='Number of thread. (Default: 0)')
    arg_parser.add_argument('input_path', help='Input directory or Input PDF file')
    arg_parser.add_argument('output_path', help='Output directory')

    args = arg_parser.parse_args()
    parser = Parser(args.backend)
    parser.parse(args.type, args.input_path, args.output_path, args.thread)
