"""Test crawler progress tracking"""
import asyncio
from backend.service.crawler_service import CrawlerService
from backend.schemas.crawler import StartCrawlerRequest

async def test_progress():
    """Test the crawler progress tracking"""
    service = CrawlerService()
    
    # Start crawler
    print("Starting crawler...")
    request = StartCrawlerRequest(mode="all", batch_size=5)
    response = await service.start_crawler(request)
    print(f"Task started: {response.task_id}")
    
    # Monitor progress for 30 seconds
    for i in range(15):
        await asyncio.sleep(2)
        status = await service.get_status()
        print(f"\n[{i*2}s] Status:")
        print(f"  Running: {status.is_running}")
        print(f"  Status: {status.status}")
        print(f"  Progress: {status.progress.crawled}/{status.progress.total}")
        print(f"  Success: {status.progress.success}, Failed: {status.progress.failed}")
        
        if not status.is_running:
            print("\nTask completed!")
            break
    
    # Final status
    final_status = await service.get_status()
    print(f"\nFinal Status:")
    print(f"  Total crawled: {final_status.progress.crawled}")
    print(f"  Success: {final_status.progress.success}")
    print(f"  Failed: {final_status.progress.failed}")

if __name__ == "__main__":
    asyncio.run(test_progress())
