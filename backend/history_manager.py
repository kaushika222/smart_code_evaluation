"""
smart-code-evaluator/backend/history_manager.py
Saves and manages code analysis history.
Version: 2.0
"""

import json
import os
import datetime
from typing import List, Dict, Any
from pathlib import Path


class HistoryManager:
    """Manages saving and loading analysis history."""
    
    def __init__(self, data_dir: str = "../data"):
        """
        Initialize history manager.
        
        Args:
            data_dir: Directory to store history files
        """
        self.data_dir = Path(data_dir)
        self.history_file = self.data_dir / "history.json"
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create history file if it doesn't exist
        if not self.history_file.exists():
            self._create_empty_history()
    
    def _create_empty_history(self):
        """Create an empty history file with proper structure."""
        empty_history = {
            "metadata": {
                "created": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
                "version": "1.0",
                "total_analyses": 0
            },
            "analyses": []
        }
        
        with open(self.history_file, 'w') as f:
            json.dump(empty_history, f, indent=2)
    
    def save_analysis(self, feedback: Dict[str, Any], 
                     code_snippet: str = "",
                     filename: str = "") -> bool:
        """
        Save an analysis to history.
        
        Args:
            feedback: Feedback dictionary from feedback.py
            code_snippet: Original code (optional)
            filename: Original filename (optional)
            
        Returns:
            True if saved successfully
        """
        try:
            # Load existing history
            history = self._load_history()
            
            # Create analysis entry
            analysis_entry = {
                "id": len(history["analyses"]) + 1,
                "timestamp": datetime.datetime.now().isoformat(),
                "language": feedback.get("language", "unknown"),
                "filename": filename,
                "skill_level": feedback.get("skill_level", "unknown"),
                "score": feedback.get("score", {}).get("score", 0),
                "grade": feedback.get("score", {}).get("grade", "N/A"),
                "total_lines": feedback.get("analysis", {}).get("total_lines", 0),
                "complexity": feedback.get("analysis", {}).get("complexity", "O(1)"),
                "mistakes_count": len(feedback.get("mistakes", [])),
                "feedback_summary": feedback.get("summary", ""),
                "code_snippet_preview": self._truncate_code(code_snippet),
                "mistake_types": [m.get("type", "unknown") for m in feedback.get("mistakes", [])]
            }
            
            # Add to history
            history["analyses"].append(analysis_entry)
            
            # Update metadata
            history["metadata"]["last_updated"] = datetime.datetime.now().isoformat()
            history["metadata"]["total_analyses"] = len(history["analyses"])
            
            # Save back to file
            self._save_history(history)
            
            print(f"✅ Analysis saved (ID: {analysis_entry['id']})")
            return True
            
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
            return False
    
    def _truncate_code(self, code: str, max_length: int = 500) -> str:
        """Truncate code snippet for storage."""
        if len(code) <= max_length:
            return code
        return code[:max_length] + "... [truncated]"
    
    def _load_history(self) -> Dict[str, Any]:
        """Load history from file."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file is corrupt, create new one
            self._create_empty_history()
            return self._load_history()
    
    def _save_history(self, history: Dict[str, Any]):
        """Save history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    
    def get_all_analyses(self) -> List[Dict[str, Any]]:
        """Get all saved analyses."""
        history = self._load_history()
        return history["analyses"]
    
    def get_analysis_by_id(self, analysis_id: int) -> Dict[str, Any]:
        """Get specific analysis by ID."""
        history = self._load_history()
        
        for analysis in history["analyses"]:
            if analysis.get("id") == analysis_id:
                return analysis
        
        return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Generate statistics from history."""
        history = self._load_history()
        analyses = history["analyses"]
        
        if not analyses:
            return {"message": "No analyses yet"}
        
        # Calculate statistics
        total_analyses = len(analyses)
        scores = [a.get("score", 0) for a in analyses]
        mistakes_counts = [a.get("mistakes_count", 0) for a in analyses]
        
        # Group by language
        languages = {}
        for analysis in analyses:
            lang = analysis.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1
        
        # Group by skill level
        skill_levels = {}
        for analysis in analyses:
            level = analysis.get("skill_level", "unknown")
            skill_levels[level] = skill_levels.get(level, 0) + 1
        
        # Common mistakes
        mistake_frequency = {}
        for analysis in analyses:
            for mistake in analysis.get("mistake_types", []):
                mistake_frequency[mistake] = mistake_frequency.get(mistake, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "best_score": max(scores) if scores else 0,
            "worst_score": min(scores) if scores else 0,
            "total_mistakes": sum(mistakes_counts),
            "average_mistakes": sum(mistakes_counts) / len(mistakes_counts) if mistakes_counts else 0,
            "languages": languages,
            "skill_levels": skill_levels,
            "common_mistakes": sorted(mistake_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "progress_over_time": self._calculate_progress(analyses)
        }
    
    def _calculate_progress(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate learning progress over time."""
        if len(analyses) < 2:
            return []
        
        # Sort by timestamp
        sorted_analyses = sorted(analyses, key=lambda x: x.get("timestamp", ""))
        
        progress = []
        for i in range(len(sorted_analyses)):
            if i >= 1:
                prev_score = sorted_analyses[i-1].get("score", 0)
                curr_score = sorted_analyses[i].get("score", 0)
                progress.append({
                    "from_id": sorted_analyses[i-1].get("id"),
                    "to_id": sorted_analyses[i].get("id"),
                    "score_change": curr_score - prev_score,
                    "improvement": curr_score > prev_score,
                    "date": sorted_analyses[i].get("timestamp", "")
                })
        
        return progress
    
    def clear_history(self) -> bool:
        """Clear all history (use with caution!)."""
        try:
            self._create_empty_history()
            print("✅ History cleared successfully")
            return True
        except Exception as e:
            print(f"❌ Error clearing history: {e}")
            return False
    
    def export_history(self, format: str = "json") -> str:
        """
        Export history in specified format.
        
        Args:
            format: "json" or "csv"
            
        Returns:
            Path to exported file
        """
        history = self._load_history()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            export_file = self.data_dir / f"history_export_{timestamp}.json"
            with open(export_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        elif format.lower() == "csv":
            export_file = self.data_dir / f"history_export_{timestamp}.csv"
            self._export_to_csv(history, export_file)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(export_file)
    
    def _export_to_csv(self, history: Dict[str, Any], export_path: Path):
        """Export history to CSV format."""
        import csv
        
        analyses = history.get("analyses", [])
        
        if not analyses:
            return
        
        # Define CSV headers
        headers = [
            "ID", "Timestamp", "Language", "Filename", "Skill Level",
            "Score", "Grade", "Total Lines", "Complexity", 
            "Mistakes Count", "Mistake Types"
        ]
        
        with open(export_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for analysis in analyses:
                row = [
                    analysis.get("id", ""),
                    analysis.get("timestamp", ""),
                    analysis.get("language", ""),
                    analysis.get("filename", ""),
                    analysis.get("skill_level", ""),
                    analysis.get("score", ""),
                    analysis.get("grade", ""),
                    analysis.get("total_lines", ""),
                    analysis.get("complexity", ""),
                    analysis.get("mistakes_count", ""),
                    ";".join(analysis.get("mistake_types", []))
                ]
                writer.writerow(row)


def test_history_manager():
    """Test the history manager."""
    print("🧪 Testing History Manager")
    print("=" * 60)
    
    # Initialize manager
    manager = HistoryManager()
    
    # Test 1: Save sample analysis
    print("\nTest 1: Saving Analysis")
    print("-" * 40)
    
    sample_feedback = {
        "timestamp": datetime.datetime.now().isoformat(),
        "language": "python",
        "skill_level": "intermediate",
        "summary": "Good code with some improvements needed",
        "analysis": {
            "total_lines": 45,
            "complexity": "O(n²)"
        },
        "score": {
            "score": 75,
            "grade": "C"
        },
        "mistakes": [
            {"type": "NESTED_LOOPS"},
            {"type": "MAGIC_NUMBERS"}
        ]
    }
    
    success = manager.save_analysis(
        feedback=sample_feedback,
        code_snippet="def test():\n    for i in range(10):\n        print(i)",
        filename="test.py"
    )
    
    if success:
        print("✅ Analysis saved successfully")
    else:
        print("❌ Failed to save analysis")
    
    # Test 2: Get all analyses
    print("\nTest 2: Get All Analyses")
    print("-" * 40)
    
    analyses = manager.get_all_analyses()
    print(f"Total analyses in history: {len(analyses)}")
    
    if analyses:
        latest = analyses[-1]
        print(f"Latest analysis:")
        print(f"  ID: {latest.get('id')}")
        print(f"  Language: {latest.get('language')}")
        print(f"  Score: {latest.get('score')}")
        print(f"  Date: {latest.get('timestamp')}")
    
    # Test 3: Get statistics
    print("\nTest 3: Get Statistics")
    print("-" * 40)
    
    stats = manager.get_statistics()
    print("📊 Statistics:")
    print(f"  Total analyses: {stats.get('total_analyses', 0)}")
    print(f"  Average score: {stats.get('average_score', 0):.1f}")
    print(f"  Best score: {stats.get('best_score', 0)}")
    print(f"  Total languages: {len(stats.get('languages', {}))}")
    
    # Test 4: Export history
    print("\nTest 4: Export History")
    print("-" * 40)
    
    try:
        export_path = manager.export_history("json")
        print(f"✅ History exported to: {export_path}")
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    return manager


def view_history():
    """View history in a nice format."""
    manager = HistoryManager()
    analyses = manager.get_all_analyses()
    
    if not analyses:
        print("📭 No history found. Analyze some code first!")
        return
    
    print("📚 ANALYSIS HISTORY")
    print("=" * 70)
    print(f"Total analyses: {len(analyses)}")
    print()
    
    for analysis in reversed(analyses[-10:]):  # Show last 10
        print(f"🔹 Analysis #{analysis.get('id')}")
        print(f"   📅 {analysis.get('timestamp', '')}")
        print(f"   💻 {analysis.get('language', 'unknown').upper()} | 📁 {analysis.get('filename', 'No file')}")
        print(f"   🎯 Level: {analysis.get('skill_level', 'unknown')}")
        print(f"   🏆 Score: {analysis.get('score', 0)}/100 ({analysis.get('grade', 'N/A')})")
        print(f"   📏 Lines: {analysis.get('total_lines', 0)} | ⚡ Complexity: {analysis.get('complexity', 'N/A')}")
        print(f"   ⚠️  Mistakes: {analysis.get('mistakes_count', 0)}")
        
        if analysis.get('mistake_types'):
            print(f"   🔍 Issues: {', '.join(analysis.get('mistake_types', []))}")
        
        print(f"   📝 Summary: {analysis.get('feedback_summary', '')[:100]}...")
        print("-" * 70)
    
    # Show statistics
    stats = manager.get_statistics()
    print("\n📈 OVERALL STATISTICS")
    print("-" * 70)
    print(f"Average Score: {stats.get('average_score', 0):.1f}/100")
    print(f"Best Score: {stats.get('best_score', 0)}/100")
    print(f"Worst Score: {stats.get('worst_score', 0)}/100")
    print(f"Total Mistakes Found: {stats.get('total_mistakes', 0)}")
    
    # Show progress
    progress = stats.get('progress_over_time', [])
    if progress:
        improvements = sum(1 for p in progress if p.get('improvement'))
        print(f"Learning Progress: {improvements}/{len(progress)} analyses showed improvement")


def integrate_with_analyzer():
    """Example of how to integrate with existing analyzer."""
    from code_reader import CodeReader
    from analyzer import CodeAnalyzer
    from mistakes import MistakeDetector
    from feedback import FeedbackGenerator
    
    # Initialize components
    reader = CodeReader()
    analyzer = CodeAnalyzer()
    detector = MistakeDetector()
    generator = FeedbackGenerator()
    history = HistoryManager()
    
    # Example file path
    file_path = input("Enter path to code file: ").strip()
    
    if not os.path.exists(file_path):
        print("❌ File not found!")
        return
    
    # Read file
    code_lines, language, error = reader.read_code_file(file_path)
    
    if error:
        print(f"❌ Error: {error}")
        return
    
    # Get original code
    with open(file_path, 'r') as f:
        original_code = f.read()
    
    # Analyze
    analysis_results = analyzer.analyze_code(code_lines, language)
    mistakes = detector.detect_mistakes(code_lines, language, analysis_results)
    feedback = generator.generate_feedback(analysis_results, mistakes, language)
    
    # Add analysis to feedback for history
    feedback["analysis"] = analysis_results
    
    # Save to history
    success = history.save_analysis(
        feedback=feedback,
        code_snippet=original_code,
        filename=os.path.basename(file_path)
    )
    
    if success:
        print("✅ Analysis saved to history!")
        
        # Show statistics
        stats = history.get_statistics()
        print(f"\n📊 Your Statistics:")
        print(f"  Total analyses: {stats.get('total_analyses', 0)}")
        print(f"  Average score: {stats.get('average_score', 0):.1f}/100")
        print(f"  Best score: {stats.get('best_score', 0)}/100")


if __name__ == "__main__":
    # Test the history manager
    test_history_manager()
    
    # Uncomment to view history
    # view_history()
    
    # Uncomment to test integration
    # integrate_with_analyzer()
    
    print("\n" + "=" * 60)
    print("📚 Available commands:")
    print("  python history_manager.py              # Run tests")
    print("  python history_manager.py --view       # View history")
    print("  python history_manager.py --stats      # Show statistics")
    print("  python history_manager.py --clear      # Clear history")
    print("  python history_manager.py --analyze    # Analyze file & save")
    print("=" * 60)