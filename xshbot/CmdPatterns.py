from typing import Sequence
import re
from abc import ABCMeta, abstractmethod


class ArgsPatternPart(metaclass=ABCMeta):
    @abstractmethod
    def number_of_args(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def validate_arg(self, args: Sequence[str], index: int) -> bool:
        raise NotImplementedError()


# コマンドの引数の長さが一致しなかった時に発生させる例外です
class CommandLengthDoesntMatchException(Exception):
    def __init__(self, length: int, help_message: str):
        self.length = length
        self.help_message = help_message

    def __str__(self):
        return "このコマンドは、少なくとも%d個の引数が必要です!" % self.length


# コマンドのパターンが一致しなかった時に発生させる例外です
class CommandArgsPatternDoesntMatchException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class NumberArgsPattern(ArgsPatternPart):
    def __init__(self, number_of_args_=1):
        self.number_of_args_ = number_of_args_

    def number_of_args(self):
        return self.number_of_args_

    def validate_arg(self, args: Sequence[str], index: int):
        i = 0
        try:
            for arg in args:
                float(arg)
            i += 1
        except ValueError:
            raise CommandArgsPatternDoesntMatchException("%d番目の引数が数値ではありません!" % (index + i + 1))
        else:
            return True


class PositiveNumberArgsPattern(ArgsPatternPart):
    def __init__(self, number_of_args_=1):
        self.number_of_args_ = number_of_args_

    def number_of_args(self):
        return self.number_of_args_

    def validate_arg(self, args: Sequence[str], index: int):
        try:
            i = 0
            for arg in args:
                f = float(arg)
                if f <= 0:
                    raise ValueError()
                i += 1
        except ValueError:
            raise CommandArgsPatternDoesntMatchException("%d番目の引数が正の数値ではありません!" % (index + 1))
        else:
            return True


class StringArgsPattern(ArgsPatternPart):
    def __init__(self, s: str):
        self.s = s

    def number_of_args(self):
        return 1

    def validate_arg(self, args: Sequence[str], index: int):
        if args[0] != self.s:
            raise CommandArgsPatternDoesntMatchException("%d番目の引数は「%s」である必要があります!" % (index + 1, self.s))
        return True


class RegexArgsPattern(ArgsPatternPart):
    def __init__(self, regex_str: str, error_message: str):
        self.regex = re.compile(regex_str)
        self.err_message = error_message

    def number_of_args(self):
        return 1

    def validate_arg(self, args: Sequence[str], index: int):
        if not self.regex.match(args[0]):
            raise CommandArgsPatternDoesntMatchException("%d番目の引数に問題があります! - %s" % (index + 1, self.err_message))
        return True
