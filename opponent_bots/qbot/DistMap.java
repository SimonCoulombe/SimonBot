import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;




public class DistMap {

	
    //private static final Map<Tile, Map <Tile, Integer> > caches = new HashMap<Tile, Map <Tile, Integer> >();

    private static final Map<Tile, DistMap > caches2 = new HashMap<Tile, DistMap >();
    private static final List<DistMap> sparecaches = new LinkedList<DistMap>();
	
    private int[][] cache;
    
    private Tile found;
    
   // private static int distcount=0;

    public void setFound(Tile it)
    {
    	found=it;
    }
    
    public Tile getFound()
    {
    	return found;
    }
    
    public DistMap(int cols, int rows)
    {
    	setCache(new int[cols][rows]);
    	emptyCache();
    	//distcount++;
    	//System.err.println("Creating DistMap #" + distcount);
    }
    
    public void emptyCache()
    {
    	found = null;
    	for (int i=0 ; i<cache.length ; i++)
        	for (int j=0 ; j<cache[i].length ; j++)
        	{
        		cache[i][j]=-1;
        	}
    }
    
    public boolean isSet(Tile tile)
    {
    	return (cache[tile.getCol()][tile.getRow()]!=-1);
    }

    public int getDistance(Tile tile)
    {
    	return cache[tile.getCol()][tile.getRow()];
    }

    public void setDistance(Tile tile, int val)
    {
    	cache[tile.getCol()][tile.getRow()]=val;
    }

	public int[][] getCache() {
		return cache;
	}

	public void setCache(int[][] cache) {
		this.cache = cache;
	}
	
	public void release()
	{
		sparecaches.add(this);
	}

    public static void emptyCaches()
    {
    	/*
		for (DistMap acache : caches2.values()) {
			sparecaches.add(acache);
		}
		*/
    	//caches.clear();

		sparecaches.addAll(caches2.values());
		caches2.clear();
    }

    public static DistMap getNewCache(Ants ants)
    {
    	DistMap retval = null;
    	if (sparecaches.size()>0)
    	{
    		retval = sparecaches.get(0);
    		sparecaches.remove(0);
    		retval.emptyCache();
    	}
    	else
    	{
    		retval = new DistMap(ants.getCols(),ants.getRows());
    	}
		return retval;
    }
    
    public static DistMap getCacheMap (Tile dest)
    {
    	DistMap cache = null;
		
		if (caches2.containsKey(dest))
		{
			cache = caches2.get(dest);
		}
		return cache;
    }

    public static void putCacheMap(DistMap cache, Tile dest)
    {
		caches2.put(dest,cache);
	}

}
