"""Tests for CLI commands."""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from prompt_manager_cli.cli import app

runner = CliRunner()


class TestNewCommand:
    """Tests for the 'new' command."""

    def test_creates_directory_if_missing(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        output_dir = tmp_path / "prompts"
        assert not output_dir.exists()

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        assert output_dir.exists()

    def test_creates_file_with_correct_name_format(self, tmp_path):
        """Test that created file has correct naming format."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc1234"):
                result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*.md"))
        assert len(files) == 1
        filename = files[0].name
        assert filename.startswith("prompt-")
        assert "-abc1234.md" in filename

    def test_creates_file_with_correct_content(self, tmp_path):
        """Test that created file has correct template content."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*.md"))
        content = files[0].read_text()

        assert "---" in content
        assert "created_at:" in content
        assert "git_hash:" in content
        assert "cwd:" in content
        assert "# Goal" in content
        assert "# Context" in content
        assert "# Constraints" in content
        assert "# Acceptance criteria" in content

    def test_uses_default_directory(self, tmp_path):
        """Test that default directory is .prompt-manager/prompts/."""
        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new"])

        assert result.exit_code == 0
        expected_dir = tmp_path / ".prompt-manager" / "prompts"
        assert expected_dir.exists()
        files = list(expected_dir.glob("prompt-*.md"))
        assert len(files) == 1

    def test_handles_filename_collision(self, tmp_path):
        """Test that collision handling works correctly."""
        output_dir = tmp_path / "prompts"
        output_dir.mkdir(parents=True)

        # Create files with same timestamp pattern
        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                # First file
                result1 = runner.invoke(app, ["new", "--dir", str(output_dir)])
                assert result1.exit_code == 0

                # Second file (should get -2 suffix since same minute)
                result2 = runner.invoke(app, ["new", "--dir", str(output_dir)])
                assert result2.exit_code == 0

        all_files = list(output_dir.glob("prompt-*.md"))
        assert len(all_files) == 2
        filenames = [f.name for f in all_files]
        assert any("-2.md" in name for name in filenames)

    def test_prints_success_message(self, tmp_path):
        """Test that success message is printed."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        assert "Created:" in result.output

    def test_edit_flag_opens_editor(self, tmp_path):
        """Test that --edit flag triggers editor."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                with patch.dict(os.environ, {"VISUAL": "vim"}):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir), "--edit"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "vim"
        assert call_args[1].endswith(".md")

    def test_edit_flag_uses_editor_fallback(self, tmp_path):
        """Test that --edit uses EDITOR if VISUAL not set."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                # Remove VISUAL if present, set only EDITOR
                env = os.environ.copy()
                env.pop("VISUAL", None)
                env["EDITOR"] = "nano"
                with patch.dict(os.environ, env, clear=True):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir), "--edit"])

        assert result.exit_code == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "nano"

    def test_edit_flag_no_editor_does_nothing(self, tmp_path):
        """Test that --edit does nothing if no editor is set."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="abc"):
                # Clear both VISUAL and EDITOR
                env = {k: v for k, v in os.environ.items() if k not in ("VISUAL", "EDITOR")}
                with patch.dict(os.environ, env, clear=True):
                    with patch("prompt_manager_cli.cli.subprocess.run") as mock_run:
                        result = runner.invoke(app, ["new", "--dir", str(output_dir), "--edit"])

        assert result.exit_code == 0
        mock_run.assert_not_called()

    def test_nogit_hash_when_not_in_repo(self, tmp_path):
        """Test that 'nogit' is used when not in a git repository."""
        output_dir = tmp_path / "prompts"

        with patch("prompt_manager_cli.cli.Path.cwd", return_value=tmp_path):
            with patch("prompt_manager_cli.cli.get_git_short_hash", return_value="nogit"):
                result = runner.invoke(app, ["new", "--dir", str(output_dir)])

        assert result.exit_code == 0
        files = list(output_dir.glob("prompt-*-nogit.md"))
        assert len(files) == 1

        content = files[0].read_text()
        assert 'git_hash: "nogit"' in content
