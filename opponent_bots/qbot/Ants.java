import java.util.*;

/**
 * Holds all game data and current game state.
 */
public class Ants {
    /** Maximum map size. */
    public static final int MAX_MAP_SIZE = 256 * 2;

    private final int loadTime;

    private final int turnTime;

    private final int rows;

    private final int cols;

    private final int turns;

    private final int viewRadius2;

    private final int attackRadius2;

    private final int spawnRadius2;

    private final boolean visible[][];

    private final Set<Tile> visionOffsets;

    private long turnStartTime;

    private final Ilk map[][];

    private final Set<Tile> myAnts = new HashSet<Tile>();

    private final Set<Tile> enemyAnts = new HashSet<Tile>();

    private final Set<Tile> myHills = new HashSet<Tile>();

    private final Set<Tile> enemyHills = new HashSet<Tile>();

    private final Set<Tile> foodTiles = new HashSet<Tile>();

    private final Set<Order> orders = new HashSet<Order>();


    /**
     * Creates new {@link Ants} object.
     * 
     * @param loadTime timeout for initializing and setting up the bot on turn 0
     * @param turnTime timeout for a single game turn, starting with turn 1
     * @param rows game map height
     * @param cols game map width
     * @param turns maximum number of turns the game will be played
     * @param viewRadius2 squared view radius of each ant
     * @param attackRadius2 squared attack radius of each ant
     * @param spawnRadius2 squared spawn radius of each ant
     */
    public Ants(int loadTime, int turnTime, int rows, int cols, int turns, int viewRadius2,
            int attackRadius2, int spawnRadius2) {
        this.loadTime = loadTime;
        this.turnTime = turnTime;
        this.rows = rows;
        this.cols = cols;
        this.turns = turns;
        this.viewRadius2 = viewRadius2;
        this.attackRadius2 = attackRadius2;
        this.spawnRadius2 = spawnRadius2;
        map = new Ilk[rows][cols];
        for (Ilk[] row : map) {
            Arrays.fill(row, Ilk.LAND);
        }
        visible = new boolean[rows][cols];
        for (boolean[] row : visible) {
            Arrays.fill(row, false);
        }
        // calc vision offsets
        visionOffsets = new HashSet<Tile>();
        int mx = (int)Math.sqrt(viewRadius2);
        for (int row = -mx; row <= mx; ++row) {
            for (int col = -mx; col <= mx; ++col) {
                int d = row * row + col * col;
                if (d <= viewRadius2) {
                    visionOffsets.add(new Tile(row, col));
                }
            }
        }
    }

    /**
     * Returns timeout for initializing and setting up the bot on turn 0.
     * 
     * @return timeout for initializing and setting up the bot on turn 0
     */
    public int getLoadTime() {
        return loadTime;
    }

    /**
     * Returns timeout for a single game turn, starting with turn 1.
     * 
     * @return timeout for a single game turn, starting with turn 1
     */
    public int getTurnTime() {
        return turnTime;
    }

    /**
     * Returns game map height.
     * 
     * @return game map height
     */
    public int getRows() {
        return rows;
    }

    /**
     * Returns game map width.
     * 
     * @return game map width
     */
    public int getCols() {
        return cols;
    }

    /**
     * Returns maximum number of turns the game will be played.
     * 
     * @return maximum number of turns the game will be played
     */
    public int getTurns() {
        return turns;
    }

    /**
     * Returns squared view radius of each ant.
     * 
     * @return squared view radius of each ant
     */
    public int getViewRadius2() {
        return viewRadius2;
    }

    /**
     * Returns squared attack radius of each ant.
     * 
     * @return squared attack radius of each ant
     */
    public int getAttackRadius2() {
        return attackRadius2;
    }

    /**
     * Returns squared spawn radius of each ant.
     * 
     * @return squared spawn radius of each ant
     */
    public int getSpawnRadius2() {
        return spawnRadius2;
    }

    /**
     * Sets turn start time.
     * 
     * @param turnStartTime turn start time
     */
    public void setTurnStartTime(long turnStartTime) {
        this.turnStartTime = turnStartTime;
    }

    /**
     * Returns how much time the bot has still has to take its turn before timing out.
     * 
     * @return how much time the bot has still has to take its turn before timing out
     */
    public int getTimeRemaining() {
        return turnTime - (int)(System.currentTimeMillis() - turnStartTime);
    }

    /**
     * Returns ilk at the specified location.
     * 
     * @param tile location on the game map
     * 
     * @return ilk at the <cod>tile</code>
     */
    public Ilk getIlk(Tile tile) {
        return map[tile.getRow()][tile.getCol()];
    }

    /**
     * Sets ilk at the specified location.
     * 
     * @param tile location on the game map
     * @param ilk ilk to be set at <code>tile</code>
     */
    public void setIlk(Tile tile, Ilk ilk) {
        map[tile.getRow()][tile.getCol()] = ilk;
    }

    /**
     * Returns ilk at the location in the specified direction from the specified location.
     * 
     * @param tile location on the game map
     * @param direction direction to look up
     * 
     * @return ilk at the location in <code>direction</code> from <cod>tile</code>
     */
    public Ilk getIlk(Tile tile, Aim direction) {
        Tile newTile = getTile(tile, direction);
        return map[newTile.getRow()][newTile.getCol()];
    }

    /**
     * Returns location in the specified direction from the specified location.
     * 
     * @param tile location on the game map
     * @param direction direction to look up
     * 
     * @return location in <code>direction</code> from <cod>tile</code>
     */
    public Tile getTile(Tile tile, Aim direction) {
        int row = (tile.getRow() + direction.getRowDelta()) % rows;
        if (row < 0) {
            row += rows;
        }
        int col = (tile.getCol() + direction.getColDelta()) % cols;
        if (col < 0) {
            col += cols;
        }
        return Tile.getTile(row, col);
    }

    /**
     * Returns location with the specified offset from the specified location.
     * 
     * @param tile location on the game map
     * @param offset offset to look up
     * 
     * @return location with <code>offset</code> from <cod>tile</code>
     */
    public Tile getTile(Tile tile, Tile offset) {
        int row = (tile.getRow() + offset.getRow()) % rows;
        if (row < 0) {
            row += rows;
        }
        int col = (tile.getCol() + offset.getCol()) % cols;
        if (col < 0) {
            col += cols;
        }
        return Tile.getTile(row, col);
    }

    /**
     * Returns a set containing all my ants locations.
     * 
     * @return a set containing all my ants locations
     */
    public Set<Tile> getMyAnts() {
        return myAnts;
    }

    /**
     * Returns a set containing all enemy ants locations.
     * 
     * @return a set containing all enemy ants locations
     */
    public Set<Tile> getEnemyAnts() {
        return enemyAnts;
    }

    /**
     * Returns a set containing all my hills locations.
     * 
     * @return a set containing all my hills locations
     */
    public Set<Tile> getMyHills() {
        return myHills;
    }

    /**
     * Returns a set containing all enemy hills locations.
     * 
     * @return a set containing all enemy hills locations
     */
    public Set<Tile> getEnemyHills() {
        return enemyHills;
    }

    /**
     * Returns a set containing all food locations.
     * 
     * @return a set containing all food locations
     */
    public Set<Tile> getFoodTiles() {
        return foodTiles;
    }

    /**
     * Returns all orders sent so far.
     * 
     * @return all orders sent so far
     */
    public Set<Order> getOrders() {
        return orders;
    }

    /**
     * Returns true if a location is visible this turn
     *
     * @param tile location on the game map
     *
     * @return true if the location is visible
     */
    public boolean isVisible(Tile tile) {
        return visible[tile.getRow()][tile.getCol()];
    }

    /**
     * Calculates distance between two locations on the game map.
     * 
     * @param t1 one location on the game map
     * @param t2 another location on the game map
     * 
     * @return distance between <code>t1</code> and <code>t2</code>
     */
    public int getDistance(Tile t1, Tile t2) {
        int rowDelta = Math.abs(t1.getRow() - t2.getRow());
        int colDelta = Math.abs(t1.getCol() - t2.getCol());
        rowDelta = Math.min(rowDelta, rows - rowDelta);
        colDelta = Math.min(colDelta, cols - colDelta);
        return rowDelta * rowDelta + colDelta * colDelta;
    }

    public int getDistanceNS(Tile t1, Tile t2) {
        int rowDelta = Math.abs(t1.getRow() - t2.getRow());
        int colDelta = Math.abs(t1.getCol() - t2.getCol());
        rowDelta = Math.min(rowDelta, rows - rowDelta);
        colDelta = Math.min(colDelta, cols - colDelta);
        return rowDelta + colDelta;
    }
    
    /**
     * Returns one or two orthogonal directions from one location to the another.
     * 
     * @param t1 one location on the game map
     * @param t2 another location on the game map
     * 
     * @return orthogonal directions from <code>t1</code> to <code>t2</code>
     */
    public List<Aim> getDirections(Tile t1, Tile t2) {
        List<Aim> directions = new ArrayList<Aim>();
        if (t1.getRow() < t2.getRow()) {
            if (t2.getRow() - t1.getRow() >= rows / 2) {
                directions.add(Aim.NORTH);
            } else {
                directions.add(Aim.SOUTH);
            }
        } else if (t1.getRow() > t2.getRow()) {
            if (t1.getRow() - t2.getRow() >= rows / 2) {
                directions.add(Aim.SOUTH);
            } else {
                directions.add(Aim.NORTH);
            }
        }
        if (t1.getCol() < t2.getCol()) {
            if (t2.getCol() - t1.getCol() >= cols / 2) {
                directions.add(Aim.WEST);
            } else {
                directions.add(Aim.EAST);
            }
        } else if (t1.getCol() > t2.getCol()) {
            if (t1.getCol() - t2.getCol() >= cols / 2) {
                directions.add(Aim.EAST);
            } else {
                directions.add(Aim.WEST);
            }
        }
        return directions;
    }

    /**
     * Clears game state information about my ants locations.
     */
    public void clearMyAnts() {
        for (Tile myAnt : myAnts) {
            map[myAnt.getRow()][myAnt.getCol()] = Ilk.LAND;
        }
        myAnts.clear();
    }

    /**
     * Clears game state information about enemy ants locations.
     */
    public void clearEnemyAnts() {
        for (Tile enemyAnt : enemyAnts) {
            map[enemyAnt.getRow()][enemyAnt.getCol()] = Ilk.LAND;
        }
        enemyAnts.clear();
    }

    /**
     * Clears game state information about food locations.
     */
    public void clearFood() {
        for (Tile food : foodTiles) {
            map[food.getRow()][food.getCol()] = Ilk.LAND;
        }
        foodTiles.clear();
    }

    /**
     * Clears game state information about my hills locations.
     */
    public void clearMyHills() {
        myHills.clear();
    }

    /**
     * Clears game state information about enemy hills locations.
     */
    public void clearEnemyHills() {
        enemyHills.clear();
    }

    /**
     * Clears game state information about dead ants locations.
     */
    public void clearDeadAnts() {
        //currently we do not have list of dead ants, so iterate over all map
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                if (map[row][col] == Ilk.DEAD) {
                    map[row][col] = Ilk.LAND;
                }
            }
        }
    }

    /**
     * Clears visible information
     */
    public void clearVision() {
        for (int row = 0; row < rows; ++row) {
            for (int col = 0; col < cols; ++col) {
                visible[row][col] = false;
            }
        }
    }

    /**
     * Calculates visible information
     */
    public void setVision() {
        for (Tile antLoc : myAnts) {
            for (Tile locOffset : visionOffsets) {
                Tile newLoc = getTile(antLoc, locOffset);
                visible[newLoc.getRow()][newLoc.getCol()] = true;
            }
        }
    }

    /**
     * Updates game state information about new ants and food locations.
     * 
     * @param ilk ilk to be updated
     * @param tile location on the game map to be updated
     */
    public void update(Ilk ilk, Tile tile) {
        map[tile.getRow()][tile.getCol()] = ilk;
        switch (ilk) {
            case FOOD:
                foodTiles.add(tile);
            break;
            case MY_ANT:
                myAnts.add(tile);
            break;
            case ENEMY_ANT:
                enemyAnts.add(tile);
            break;
            case WATER:
            	DistMap.emptyCaches();
            break;
        }
    }

    /**
     * Updates game state information about hills locations.
     *
     * @param owner owner of hill
     * @param tile location on the game map to be updated
     */
    public void updateHills(int owner, Tile tile) {
        if (owner > 0)
            enemyHills.add(tile);
        else
            myHills.add(tile);
    }

    /**
     * Issues an order by sending it to the system output.
     * 
     * @param myAnt map tile with my ant
     * @param direction direction in which to move my ant
     */
    public void issueOrder(Tile myAnt, Aim direction) {
        Order order = new Order(myAnt, direction);
        orders.add(order);
        System.out.println(order);
    }

    public Map<Tile, Integer> makeDistanceMap (Tile start, Tile dest, boolean full)
    {
		int moves = 0;
		//int numdir = 0;
	
		Map <Tile, Integer> cache = new HashMap<Tile,Integer>();
	
		Set <Tile> todo = null;
		Set <Tile> nextTodo = new HashSet<Tile>();
	
		nextTodo.add(dest);
		cache.put(dest,moves);	
	
		while ( ((full) || (!cache.containsKey(start))) && (nextTodo.size()>0) )
		{
			todo=nextTodo;
			nextTodo=new HashSet<Tile>();
			moves++;
	//	System.err.println("Starting iteration " + new Integer(moves));
			for (Tile todoPoint : todo) {
	//	System.err.println("Considering " + todoPoint);
				//for (Aim direction : Aim.values()) {
				for (Aim direction : Aim.getStaticValues()) {
					//numdir++;
					Tile newLoc = getTile(todoPoint, direction);
					if (!getIlk(newLoc).isPassable())
					{
						continue;
					}
	//	System.err.println("Now at " + newLoc);
					if (cache.containsKey(newLoc))
					{
	//	System.err.println("Already been here");
						continue;
					}
					nextTodo.add(newLoc);
					cache.put(newLoc,new Integer(moves));	
				}
			}
		}
		//System.err.println("Took " + moves + " steps in " + numdir + " directions");
	
		return cache;
    }

    public DistMap makeDistanceMap2 (Tile point, Tile toFindPoint, Set<Tile> toFind, int limit)
    {
		int moves = 0;
	
		DistMap cache = DistMap.getNewCache(this);
	
		List <Tile> todo = new ArrayList<Tile>();
		List <Tile> nextTodo = new ArrayList<Tile>();
	
		nextTodo.add(point.copyof());
		cache.setDistance(point,moves);	
	
		boolean doneSearching = false;
		if (toFind!=null)
		{
			doneSearching = toFind.contains(point);
		}
		
		if (doneSearching)
			cache.setFound(point);
		
		while (!doneSearching)
		{
			List <Tile> temp = todo;
			todo=nextTodo;
			temp.clear();
			nextTodo=temp;
			moves++;

			doneSearching=false;
			
			for (Tile todoPoint : todo) {
	//	System.err.println("Considering " + todoPoint);
				//for (Aim direction : Aim.values()) {
				for (Aim direction : Aim.getStaticValues()) {
					Tile newLoc = getTile(todoPoint, direction);
					if (!getIlk(newLoc).isPassable())
					{
						newLoc.done();
						continue;
					}
	//	System.err.println("Now at " + newLoc);
					if (cache.isSet(newLoc))
					{
	//	System.err.println("Already been here");
						newLoc.done();
						continue;
					}
					if ((!doneSearching) && (toFind!=null))
					{
						doneSearching = toFind.contains(newLoc);
						if (doneSearching)
						{	
							//System.err.println("Found " + newLoc + " from " + point);
							cache.setFound(newLoc.copyof());
						}
					}
					if ((!doneSearching) && (toFindPoint!=null))
					{
						doneSearching = toFindPoint.equals(newLoc);
						if (doneSearching)
							cache.setFound(newLoc.copyof());
					}
					nextTodo.add(newLoc);
					cache.setDistance(newLoc, moves);	
				}
				todoPoint.done();
			}
			
			if (!doneSearching)
			{
				doneSearching=((nextTodo.size()==0) || (moves>limit));
				if (doneSearching)
				{
					cache.setFound(null);
					//System.err.println("Giving up since todo=" + nextTodo.size() + " or " + moves + ">" + limit);
				}
			}
		}
		//System.err.println("Took " + moves + " steps in " + numdir + " directions");
	
		return cache;
    }


    

    /*
    public Map<Tile, Integer> getDistanceMap (Tile start, Tile dest)
    {
		Map <Tile, Integer> cache = null;
	
		//int starttime = (int)(System.currentTimeMillis());
	
		if (caches.containsKey(dest))
		{
			cache = caches.get(dest);
			//System.err.println("Cache hit " + cache.size() + " in " + ((int)(System.currentTimeMillis() - starttime)));
			return cache;
		}
		else
		{
			cache = makeDistanceMap(start, dest, true);
	
			caches.put(dest,cache);
			//System.err.println("Cache miss " + cache.size() + " in " + ((int)(System.currentTimeMillis() - starttime)));
	
			return cache;
		}
    }
    */

    public DistMap getDistanceMap2 (Tile start, Tile dest)
    {
    	DistMap cache = DistMap.getCacheMap(dest);
	
		//int starttime = (int)(System.currentTimeMillis());
	
		if (cache!=null)
		{
			//System.err.println("Cache hit " + cache.size() + " in " + ((int)(System.currentTimeMillis() - starttime)));
			return cache;
		}
		else
		{
			cache = makeDistanceMap2(dest, null, null, 999);
	
			DistMap.putCacheMap(cache, dest);
			//System.err.println("Cache miss " + cache.size() + " in " + ((int)(System.currentTimeMillis() - starttime)));
	
			return cache;
		}
    }
    
    public List<Aim> findNearest(Tile start, Set<Tile> what)
    {
		List<Aim> returnarr = new ArrayList<Aim>();
		
    	// find the nearest one
    	DistMap cache = makeDistanceMap2(start, null, what, 60);

    	if (cache.getFound()==null)
    	{
			//System.err.println("Not found " + start + " finding " + what.size());
    		return returnarr;
    	}
    	
    	// now find it from us so we can get the directions
    	DistMap cache2 = makeDistanceMap2(cache.getFound(), start, null, 999);

		int min=999;
	
		for (Aim direction : Aim.getStaticValues()) {
			Tile newLoc = getTile(start, direction);
			if (cache2.isSet(newLoc))
				if (cache2.getDistance(newLoc)<=min)
				{
					if (cache2.getDistance(newLoc)<min)
					{
						returnarr.clear();
						min=cache.getDistance(newLoc);
					}
					returnarr.add(direction);
				}
		}
	
		cache.release();
		cache2.release();
		//System.err.println("Found " + returnarr.size() + " directions");
		return returnarr;	
    }
    
    public int getDistance2(Tile t1, Tile t2) {
    	//Map <Tile, Integer> cache = getDistanceMap(t1, t2);
    	DistMap cache = getDistanceMap2(t1, t2);

		Integer dist = 999;
	
		//if (cache.containsKey(t1))
			//dist = cache.get(t1);
		if (cache.isSet(t1))
			dist = cache.getDistance(t1);
		//System.err.println("From " + t1 + ", to " + t2 + ", is " + dist);

		return dist;
    }

    public List<Aim> getDirections2(Tile t1, Tile t2) {
		int min=999;
	
		//Map <Tile, Integer> cache = getDistanceMap(t1, t2);
		DistMap cache = getDistanceMap2(t1, t2);
		LinkedList<Aim> returnarr = new LinkedList<Aim>();
	
		for (Aim direction : Aim.values()) {
			Tile newLoc = getTile(t1, direction);
			/*
			if (cache.containsKey(newLoc))
				if (cache.get(newLoc).intValue()<=min)
				{
					if (cache.get(newLoc).intValue()<min)
					{
						returnarr.clear();
						min=cache.get(newLoc).intValue();
					}
					returnarr.add(direction);
				}
			*/
			if (cache.isSet(newLoc))
			{
				if (cache.getDistance(newLoc)<=min)
				{
					if (cache.getDistance(newLoc)<min)
					{
						//returnarr.clear();
						min=cache.getDistance(newLoc);
					}
					returnarr.addFirst(direction);
				}
				else
				{
					returnarr.addLast(direction);
				}
			}
		}
	
		return returnarr;
    }


}
