import asyncio
import importlib
from src.adk.models.app import AppActionCore, AppActionEntity
from src.constants import SYSTEM_USER
import typer
from pathlib import Path
from src.adk.registry.app_registry import AppRegistry
from src.db.session import get_session
from src.crud.app import app as app_crud
from src.crud.app_action import app_action as app_action_crud

cli = typer.Typer()

def import_app_definitions():
    """Automatically import all app definitions"""
    apps_dir = Path(__file__).parent.parent / "apps"
    
    for app_dir in apps_dir.iterdir():
        if not app_dir.is_dir():
            continue
            
        for version_dir in app_dir.iterdir():
            if not version_dir.is_dir():
                continue
                
            # Convert path to module path
            module_path = str(version_dir / "definition.py")
            if not Path(module_path).exists():
                continue

            # Convert file path to module path
            relative_path = version_dir.relative_to(Path(__file__).parent.parent)
            module_name = ".".join(relative_path.parts)

            try:
                importlib.import_module(f"src.{module_name}.definition")
            except Exception as e:
                print(f"Error importing {module_name}: {e}")

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
                db_app = await app_crud.create_or_update_no_commit(session=session, obj_in=app_definition, user=SYSTEM_USER)
                # Create actions
                for action in app_definition.actions:
                    action_core = AppActionCore(
                        name=action.name,
                        description=action.description,
                        appId=db_app.id,
                        appVersion=app_definition.version,
                        actionType=action.actionType,
                        dataSchema=action.dataSchema,
                        uiSchema=action.uiSchema,
                    )
                    await app_action_crud.create_or_update_no_commit(session=session, obj_in=action_core, user=SYSTEM_USER)
            await session.commit()
    asyncio.run(_sync())

if __name__ == "__main__":
    cli() 