import asyncio
import importlib
import typer
from pathlib import Path
from src.adk.registry.app_registry import AppRegistry
from src.db.session import get_session
from src.crud.app import app

cli = typer.Typer()

def import_app_definitions():
    """Automatically import all app definitions recursively"""
    apps_dir = Path(__file__).parent.parent / "apps"

    def scan_directory(directory: Path):
        for path in directory.iterdir():
            if path.is_dir():
                # Check if definition.py exists in current directory
                definition_file = path / "definition.py"
                if definition_file.exists():
                    # Convert file path to module path
                    relative_path = path.relative_to(Path(__file__).parent.parent)
                    module_name = ".".join(relative_path.parts)
                    
                    try:
                        importlib.import_module(f"src.{module_name}.definition")
                    except Exception as e:
                        print(f"Error importing {module_name}: {e}")
                
                # Recursively scan subdirectories
                scan_directory(path)
    
    scan_directory(apps_dir)

@cli.command()
def sync_apps():
    """Sync app definitions from code to database"""
    async def _sync():
        # Import all app definitions
        import_app_definitions()
        
        # Get registered apps
        apps = AppRegistry().get_all_apps()
        
        async for session in get_session():
            for app_definition in apps:
                await app.create_or_update(session=session, obj_in=app_definition)
    
    asyncio.run(_sync())

if __name__ == "__main__":
    cli()
