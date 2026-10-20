"""
Test cases for main.py - Interactive REPL for code questions and session management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from io import StringIO
import sys


class TestGetOrCreateIndex:
    """Test cases for get_or_create_index function."""

    @patch('main.get_indexer')
    @patch('main.Path')
    def test_get_or_create_index_success(self, mock_path, mock_get_indexer):
        """Test successful index creation/retrieval."""
        from main import get_or_create_index

        # Setup
        mock_indexer_func = Mock(return_value={'indexed': True})
        mock_get_indexer.return_value = mock_indexer_func
        mock_path.cwd.return_value = Path('/test/repo')

        # Execute
        result = get_or_create_index()

        # Assert
        assert result == {'indexed': True}
        mock_get_indexer.assert_called_once()
        mock_indexer_func.assert_called_once_with('/test/repo')

    @patch('main.get_indexer')
    @patch('main.Path')
    @patch('main.console')
    def test_get_or_create_index_prints_console_message(self, mock_console, mock_path, mock_get_indexer):
        """Test that get_or_create_index logs to console."""
        from main import get_or_create_index

        # Setup
        mock_indexer_func = Mock(return_value={})
        mock_get_indexer.return_value = mock_indexer_func
        mock_path.cwd.return_value = Path('/test/repo')

        # Execute
        get_or_create_index()

        # Assert
        assert mock_console.print.called


class TestInitialize:
    """Test cases for initialize function."""

    @patch('main.get_current_session')
    @patch('main.get_or_create_index')
    @patch('main.config')
    @patch('main.console')
    def test_initialize_success(self, mock_console, mock_config, mock_get_index, mock_get_session):
        """Test successful initialization."""
        from main import initialize

        # Setup
        mock_config.__getitem__.side_effect = lambda key: {
            'llm': {'provider': 'anthropic', 'model': 'claude-3'},
            'embeddings': {'provider': 'openai', 'model': 'text-embedding-3-small'}
        }[key]
        mock_get_index.return_value = Mock(name='index_mock')
        mock_get_session.return_value = 'session-123'

        # Execute
        index, session_id = initialize()

        # Assert
        assert index == mock_get_index.return_value
        assert session_id == 'session-123'
        mock_get_index.assert_called_once()
        mock_get_session.assert_called_once()

    @patch('main.get_current_session')
    @patch('main.get_or_create_index')
    @patch('main.config')
    @patch('main.console')
    def test_initialize_logs_config(self, mock_console, mock_config, mock_get_index, mock_get_session):
        """Test that initialize logs configuration details."""
        from main import initialize

        # Setup
        mock_config.__getitem__.side_effect = lambda key: {
            'llm': {'provider': 'anthropic', 'model': 'claude-3'},
            'embeddings': {'provider': 'openai', 'model': 'text-embedding-3-small'}
        }[key]
        mock_get_index.return_value = Mock()
        mock_get_session.return_value = 'session-123'

        # Execute
        initialize()

        # Assert - Verify console.print was called with configuration
        assert mock_console.print.call_count >= 3  # LLM, Embedder, Session info


class TestRun:
    """Test cases for run function."""

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_exit_command(self, mock_console, mock_initialize, mock_prompt):
        """Test that /exit command terminates the REPL."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/exit']

        # Execute
        run()

        # Assert
        mock_console.print.assert_called_with('[dim]Goodbye![/dim]')

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_quit_command(self, mock_console, mock_initialize, mock_prompt):
        """Test that /quit command terminates the REPL."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/quit']

        # Execute
        run()

        # Assert
        mock_console.print.assert_called_with('[dim]Goodbye![/dim]')

    @patch('main.Prompt.ask')
    @patch('main.handle_query')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_ask_command(self, mock_console, mock_initialize, mock_handle_query, mock_prompt):
        """Test that /ask command handles queries correctly."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_handle_query.return_value = 'Answer to the question'
        mock_prompt.side_effect = ['/ask what is this code?', '/exit']

        # Execute
        run()

        # Assert
        mock_handle_query.assert_called_once_with('what is this code?', 'session-123')
        mock_console.print.assert_any_call('Answer to the question')

    @patch('main.Prompt.ask')
    @patch('main.new_session')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_new_session_command(self, mock_console, mock_initialize, mock_new_session, mock_prompt):
        """Test that /new_session command creates a new session."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_new_session.return_value = 'session-456'
        mock_prompt.side_effect = ['/new_session', '/exit']

        # Execute
        run()

        # Assert
        mock_new_session.assert_called_once()
        assert mock_console.print.call_count >= 1

    @patch('main.Prompt.ask')
    @patch('main.switch_session')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_switch_session_command(self, mock_console, mock_initialize, mock_switch_session, mock_prompt):
        """Test that /switch command switches to a different session."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_switch_session.return_value = 'session-789'
        mock_prompt.side_effect = ['/switch session-789', '/exit']

        # Execute
        run()

        # Assert
        mock_switch_session.assert_called_once_with('session-789')

    @patch('main.Prompt.ask')
    @patch('main.switch_session')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_switch_session_without_id(self, mock_console, mock_initialize, mock_switch_session, mock_prompt):
        """Test that /switch without session_id shows usage message."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/switch ', '/exit']

        # Execute
        run()

        # Assert
        # Verify usage message was printed
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any('Usage' in str(c) for c in calls)

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_session_command(self, mock_console, mock_initialize, mock_prompt):
        """Test that /session command displays the current session."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/session', '/exit']

        # Execute
        run()

        # Assert
        mock_console.print.assert_any_call('[dim]Current session: session-123[/dim]')

    @patch('main.Prompt.ask')
    @patch('main.get_index_inspector')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_show_index_command(self, mock_console, mock_initialize, mock_get_inspector, mock_prompt):
        """Test that /show_index command displays the index."""
        from main import run

        # Setup
        mock_index = Mock()
        mock_initialize.return_value = (mock_index, 'session-123')
        mock_inspector = Mock()
        mock_get_inspector.return_value = mock_inspector
        mock_prompt.side_effect = ['/show_index', '/exit']

        # Execute
        run()

        # Assert
        mock_get_inspector.assert_called_once()
        mock_inspector.assert_called_once_with(mock_index)

    @patch('main.Prompt.ask')
    @patch('main.get_index_inspector')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_show_semantic_index_command(self, mock_console, mock_initialize, mock_get_inspector, mock_prompt):
        """Test that /show_semantic_index command displays the index."""
        from main import run

        # Setup
        mock_index = Mock()
        mock_initialize.return_value = (mock_index, 'session-123')
        mock_inspector = Mock()
        mock_get_inspector.return_value = mock_inspector
        mock_prompt.side_effect = ['/show_semantic_index', '/exit']

        # Execute
        run()

        # Assert
        mock_inspector.assert_called_once_with(mock_index)

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_empty_input(self, mock_console, mock_initialize, mock_prompt):
        """Test that empty input is skipped."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['', '  ', '/exit']

        # Execute
        run()

        # Assert - Should just exit without errors
        assert True

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_unknown_command(self, mock_console, mock_initialize, mock_prompt):
        """Test that unknown command shows help message."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/unknown_command', '/exit']

        # Execute
        run()

        # Assert
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any('Unknown command' in str(c) for c in calls)

    @patch('main.Prompt.ask')
    @patch('main.handle_query')
    @patch('main.initialize')
    @patch('main.console')
    def test_run_ask_command_with_no_text(self, mock_console, mock_initialize, mock_handle_query, mock_prompt):
        """Test that /ask with no question is handled gracefully."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_handle_query.return_value = 'Response'
        mock_prompt.side_effect = ['/ask ', '/exit']

        # Execute
        run()

        # Assert - Should handle empty question
        mock_handle_query.assert_called_once()

    @patch('main.Prompt.ask')
    @patch('main.initialize')
    @patch('main.logger')
    def test_run_logs_startup(self, mock_logger, mock_initialize, mock_prompt):
        """Test that startup is logged."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_prompt.side_effect = ['/exit']

        # Execute
        run()

        # Assert
        mock_logger.info.assert_called()


class TestIntegration:
    """Integration tests for main.py components working together."""

    @patch('main.Prompt.ask')
    @patch('main.handle_query')
    @patch('main.get_current_session')
    @patch('main.get_or_create_index')
    @patch('main.config')
    @patch('main.console')
    def test_run_full_workflow(self, mock_console, mock_config, mock_get_index, 
                                mock_get_session, mock_handle_query, mock_prompt):
        """Test complete workflow: initialize and handle queries."""
        from main import run

        # Setup
        mock_config.__getitem__.side_effect = lambda key: {
            'llm': {'provider': 'anthropic', 'model': 'claude-3'},
            'embeddings': {'provider': 'openai', 'model': 'text-embedding-3-small'}
        }[key]
        mock_get_index.return_value = Mock()
        mock_get_session.return_value = 'session-123'
        mock_handle_query.return_value = 'Query result'
        mock_prompt.side_effect = [
            '/ask explain this code',
            '/session',
            '/exit'
        ]

        # Execute
        run()

        # Assert
        mock_handle_query.assert_called_once_with('explain this code', 'session-123')
        assert mock_console.print.call_count >= 5  # Startup messages + results


class TestAskCommandParsing:
    """Test parsing of /ask command."""

    @patch('main.Prompt.ask')
    @patch('main.handle_query')
    @patch('main.initialize')
    @patch('main.console')
    def test_ask_command_with_special_characters(self, mock_console, mock_initialize, 
                                                   mock_handle_query, mock_prompt):
        """Test /ask command with special characters in question."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_handle_query.return_value = 'Answer'
        question = 'what does this return: {"key": "value"}'
        mock_prompt.side_effect = [f'/ask {question}', '/exit']

        # Execute
        run()

        # Assert
        mock_handle_query.assert_called_once_with(question, 'session-123')

    @patch('main.Prompt.ask')
    @patch('main.handle_query')
    @patch('main.initialize')
    @patch('main.console')
    def test_ask_command_with_multiword_question(self, mock_console, mock_initialize, 
                                                   mock_handle_query, mock_prompt):
        """Test /ask command with long multi-word question."""
        from main import run

        # Setup
        mock_initialize.return_value = (Mock(), 'session-123')
        mock_handle_query.return_value = 'Answer'
        question = 'how does the authentication middleware validate tokens and handle refresh flows'
        mock_prompt.side_effect = [f'/ask {question}', '/exit']

        # Execute
        run()

        # Assert
        mock_handle_query.assert_called_once_with(question, 'session-123')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
