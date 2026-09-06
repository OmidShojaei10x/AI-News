"""Tests for RTL text formatting."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.rtl_text import LRI, PDI, RLM, fix_rtl


def test_fix_rtl_adds_rlm():
    result = fix_rtl("سلام")
    assert result.startswith(RLM)


def test_fix_rtl_isolates_latin():
    result = fix_rtl("مدل Astra منتشر شد")
    assert f"{LRI}Astra{PDI}" in result


def test_fix_rtl_preserves_html():
    result = fix_rtl("<b>مدل OpenAI</b>")
    assert "<b>" in result
    assert f"{LRI}OpenAI{PDI}" in result


def test_fix_rtl_idempotent():
    text = "مدل GPT-6 Astra منتشر شد"
    once = fix_rtl(text)
    twice = fix_rtl(once)
    assert once == twice


if __name__ == "__main__":
    test_fix_rtl_adds_rlm()
    test_fix_rtl_isolates_latin()
    test_fix_rtl_preserves_html()
    test_fix_rtl_idempotent()
    print("All RTL tests passed.")
