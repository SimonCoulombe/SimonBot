import java.io.IOException;
import java.util.*;

/**
 * Starter bot implementation.
 */
public class MyBot extends Bot {
    /**
     * Main method executed by the game engine for starting the bot.
     * 
     * @param args command line arguments
     * 
     * @throws IOException if an I/O error occurs
     */
    public static void main(String[] args) throws IOException {
        new MyBot().readSystemInput();
    }

    private Map<Tile, Tile> orders = new HashMap<Tile, Tile>();
    Set<Tile> lazyAnts = new HashSet<Tile>();

    private Set<Tile> unseenTiles;

    private Set<Tile> enemyHills = new HashSet<Tile>();

	private boolean goon=false;
	private boolean debug=false;
	private boolean loading=false;
	private boolean timing=false;
	private boolean unseendebug=false;
    
    private boolean doMoveDirection(Tile antLoc, Aim direction) {
        Ants ants = getAnts();
        // Track all moves, prevent collisions
        Tile newLoc = ants.getTile(antLoc, direction);
        Ilk destIlk = ants.getIlk(newLoc);
        boolean domove=false;
	    if (orders.containsKey(newLoc))
	    {
	    	if (goon)
	    		System.err.println("Can't move " + direction + " as another ant is going there");
	    }
	    else if (destIlk.isUnoccupied())
	    {
	    	// no ant moving to it, and its unoccupied
        	domove=true;
        }
	    else 
	    {
	    	// no ant moving to it, but it is occupied
		    if (destIlk==Ilk.MY_ANT)
		    {
		    	// let see if the ant is moving
		    	if (orders.containsValue(newLoc))
		    	{
		    		// yes its moving, so we can move to it
		    		domove=true;
		    		// technically if it get blocked then we will destroy ourselves,
		    		// but that should only happen if a food spawns so quite unlikely
		    	}
		    	else
		    	{
					if (goon)
				    	System.err.println("Can't move " + direction + " one of my ants won't get out the way");
		    	}
		    }
		    else
			{
		    	// occupied by something i can't contol
				if (goon)
			    	System.err.println("Can't move " + direction + " as its full of " + destIlk);
			}
        }
	    
        if (domove)
        {
            ants.issueOrder(antLoc, direction);
            orders.put(newLoc, antLoc);
            lazyAnts.remove(antLoc);
        }
        return domove;
    }

    private boolean doMoveLocation(Tile antLoc, Tile destLoc) {
        Ants ants = getAnts();
        // Track targets to prevent 2 ants to the same location
        List<Aim> directions = ants.getDirections2(antLoc, destLoc);
        for (Aim direction : directions) {
            if (doMoveDirection(antLoc, direction)) {
                return true;
            }
        }
		if (goon)
		{
			System.err.println("Couldn't find a direction to move " + antLoc + ", " +  destLoc + " from " + directions.size());
			for (Aim direction : directions) {
				System.err.println("Tried " + direction);
			}
		}
        return false;
    }

    @Override
    public void doTurn() {
        Ants ants = getAnts();

		int time_r=ants.getTimeRemaining();
		if (timing)
		{	
			System.err.println("Start " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
			time_r=ants.getTimeRemaining();
		}

        orders.clear();
        Map<Tile, Tile> foodTargets = new HashMap<Tile, Tile>();
        lazyAnts.clear();
        lazyAnts.addAll(ants.getMyAnts());

        // add all locations to unseen tiles set, run once
        if (unseenTiles == null) {
            unseenTiles = new HashSet<Tile>();
            for (int row = 0; row < ants.getRows(); row++) {
                for (int col = 0; col < ants.getCols(); col++) {
                    unseenTiles.add(new Tile(row, col));
                }
            }
        }
        // remove any tiles that can be seen, run each turn
        for (Iterator<Tile> locIter = unseenTiles.iterator(); locIter.hasNext(); ) {
            Tile next = locIter.next();
            if (ants.isVisible(next)) {
                locIter.remove();
            }
        }

        // prevent stepping on own hill
        for (Tile myHill : ants.getMyHills()) {
            orders.put(myHill, null);
        }

        if (ants.getMyAnts().size() - (4*ants.getMyHills().size())>15)
        {
            for (Tile myHill : ants.getMyHills()) {
            	Tile u1 = ants.getTile(myHill, Aim.NORTH);
            	Tile u1_e1 = ants.getTile(u1, Aim.EAST);
            	Tile u1_w1 = ants.getTile(u1, Aim.WEST);
            	lazyAnts.remove(u1_e1);
            	lazyAnts.remove(u1_w1);
            	Tile d1 = ants.getTile(myHill, Aim.SOUTH);
            	Tile d1_e1 = ants.getTile(d1, Aim.EAST);
            	Tile d1_w1 = ants.getTile(d1, Aim.WEST);
            	lazyAnts.remove(d1_e1);
            	lazyAnts.remove(d1_w1);
            	if ((true) && (ants.getMyAnts().size() - (16*ants.getMyHills().size())>15))
                {
                	Tile u1_e2 = ants.getTile(u1_e1, Aim.EAST);
                	Tile u1_w2 = ants.getTile(u1_w1, Aim.WEST);
                	lazyAnts.remove(u1_e2);
                	lazyAnts.remove(u1_w2);
                	Tile d1_e2 = ants.getTile(d1_e1, Aim.EAST);
                	Tile d1_w2 = ants.getTile(d1_w1, Aim.WEST);
                	lazyAnts.remove(d1_e2);
                	lazyAnts.remove(d1_w2);
                	Tile u2 = ants.getTile(u1, Aim.NORTH);
                	Tile u2_e1 = ants.getTile(u2, Aim.EAST);
                	Tile u2_w1 = ants.getTile(u2, Aim.WEST);
                	lazyAnts.remove(u2_e1);
                	lazyAnts.remove(u2_w1);
                	Tile d2 = ants.getTile(d1, Aim.SOUTH);
                	Tile d2_e1 = ants.getTile(d2, Aim.EAST);
                	Tile d2_w1 = ants.getTile(d2, Aim.WEST);
                	lazyAnts.remove(d2_e1);
                	lazyAnts.remove(d2_w1);
                	Tile u2_e2 = ants.getTile(u2_e1, Aim.EAST);
                	Tile u2_w2 = ants.getTile(u2_w1, Aim.WEST);
                	lazyAnts.remove(u2_e2);
                	lazyAnts.remove(u2_w2);
                	Tile d2_e2 = ants.getTile(d2_e1, Aim.EAST);
                	Tile d2_w2 = ants.getTile(d2_w1, Aim.WEST);
                	lazyAnts.remove(d2_e2);
                	lazyAnts.remove(d2_w2);
                }
            }
        }

        if (timing)
		{	
			System.err.println("Init " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
			time_r=ants.getTimeRemaining();
		}
        
        if (lazyAnts.size()>5)
        {
            for (Tile myHill : ants.getMyHills()) {
                for (Tile antLoc : lazyAnts.toArray(new Tile[0]))
                {
                	if (myHill.equals(antLoc))
                	{
                		continue;
                	}
                	int dist = ants.getDistanceNS(antLoc, myHill);
                	if (dist<=3)
                	{
            			//System.err.println("Found nearby " + dist + " at " + antLoc + " near " + myHill);
            			Aim toGo = null;
                		
                		// move ants close to the hill away in the direction they are going
                		if (antLoc.getCol()==myHill.getCol())
                		{
                			int diff = antLoc.getRow()-myHill.getRow();
                    		if (diff<0 || diff>5) // >5 is its wrapped
                    			toGo=Aim.NORTH;
                    		else
                    			toGo=Aim.SOUTH;
                		}
                		if (antLoc.getRow()==myHill.getRow())
                		{
                			int diff = antLoc.getCol()-myHill.getCol();
                    		if (diff<0 || diff>5) // >5 is its wrapped
                    			toGo=Aim.WEST;
                    		else
                    			toGo=Aim.EAST;
                		}
                		if (toGo!=null)
                		{
                			//goon=true;
                	        //Tile newLoc = ants.getTile(antLoc, toGo);
                			doMoveDirection(antLoc, toGo);
                			//goon=false;
                			//System.err.println("Going " + toGo + " to " + newLoc);
                		}
                	}
                }
            }
            for (int i=2;i<=3;i++)
            {
                for (Tile myHill : ants.getMyHills())
                {
                	orders.put(ants.getTile(myHill,new Tile(0,i)), null);
                	orders.put(ants.getTile(myHill,new Tile(i,0)), null);
                }
            }
        }
        
        // find close food
        List<Route> foodRoutes = new ArrayList<Route>();
        TreeSet<Tile> sortedFood = new TreeSet<Tile>(ants.getFoodTiles());
        for (Tile foodLoc : sortedFood) {
            for (Tile antLoc : lazyAnts) {
                int distance = ants.getDistance2(antLoc, foodLoc);
                Route route = new Route(antLoc, foodLoc, distance);
                foodRoutes.add(route);
            }
        }
        Collections.sort(foodRoutes);
        for (Route route : foodRoutes) {
            if (!foodTargets.containsKey(route.getEnd())
                    && !foodTargets.containsValue(route.getStart())
                    && doMoveLocation(route.getStart(), route.getEnd())) {
                foodTargets.put(route.getEnd(), route.getStart());
            }
        }

		if (timing)
		{	
			System.err.println("After food " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
			time_r=ants.getTimeRemaining();
		}
	
		// remove any enemy hills we are on
        for (Tile antLoc : ants.getMyAnts()) {
            if (enemyHills.contains(antLoc)) {
            	enemyHills.remove(antLoc);
            }
        }

        // add new hills to set
        for (Tile enemyHill : ants.getEnemyHills()) {
            if (!enemyHills.contains(enemyHill)) {
                enemyHills.add(enemyHill);
            }
        }
        // attack hills
        List<Route> hillRoutes = new ArrayList<Route>();
        for (Tile hillLoc : enemyHills) {
            for (Tile antLoc : lazyAnts) {
                int distance = ants.getDistance2(antLoc, hillLoc);
                Route route = new Route(antLoc, hillLoc, distance);
                hillRoutes.add(route);
            }
        }
        Collections.sort(hillRoutes);
        for (Route route : hillRoutes) {
            if (lazyAnts.contains(route.getStart())) {
				if ((route.getDistance()<2) && (debug))
				{
					System.err.println("Moving ant to hill " + route.getStart() + ", " +  route.getEnd() + " in " + route.getDistance());
					goon=true;
				}
				doMoveLocation(route.getStart(), route.getEnd());
            }
        }

		if (timing)
		{	
			System.err.println("After hills " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
			time_r=ants.getTimeRemaining();
		}
		
	    if (unseendebug)
	    	System.err.println("unseenTiles " + unseenTiles.size() + " lazyAnts " + lazyAnts.size());
		
		int bored_ants=0;
		
        // explore unseen areas
        for (Tile antLoc : lazyAnts.toArray(new Tile[0])) {
			if (ants.getTimeRemaining()<100)
			{
				if (timing)
					System.err.println("Low remaining time giving up 1");
				break;
			}
			bored_ants++;
			if (loading)
				System.err.println("bored_ants " + bored_ants + " remain " + ants.getTimeRemaining());
			
	        List<Aim> directions = ants.findNearest(antLoc, unseenTiles);
	        for (Aim direction : directions) {
	            if (doMoveDirection(antLoc, direction)) {
	    			//System.err.println("Take the move " + direction);
	                break;
	            }
	        }
        }
		
        // explore unseen areas
        /*
        for (Tile antLoc : lazyAnts.toArray(new Tile[0])) {
			if (ants.getTimeRemaining()<100)
			{
				if (timing)
					System.err.println("Low remaining time giving up 1");
				break;
			}
			bored_ants++;
			if (loading)
				System.err.println("bored_ants " + bored_ants + " remain " + ants.getTimeRemaining());
            List<Route> unseenRoutes = new ArrayList<Route>();
            for (Tile unseenLoc : unseenTiles) {
            	int distance=999;
            	//if (unseenTiles.size()<50)
            		distance = ants.getDistance2(unseenLoc, antLoc);
            	//else
            		//distance = ants.getDistance(antLoc, unseenLoc);
            		
                Route route = new Route(antLoc, unseenLoc, distance);
                unseenRoutes.add(route);
				if (ants.getTimeRemaining()<100)
				{
					if (timing)
						System.err.println("Low remaining time giving up 2");
					break;
				}
            }
            Collections.sort(unseenRoutes);
            for (Route route : unseenRoutes) {
				if (loading)
					System.err.println("before");
                if (doMoveLocation(route.getStart(), route.getEnd())) {
					if (loading)
						System.err.println("after1");
                        break;
                }
				if (loading)
					System.err.println("after2");
                    break;
            }
        }
        */

		if (timing)
		{	
			System.err.println("After unseen " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
			time_r=ants.getTimeRemaining();
		}
	
	    if (unseendebug)
	    	System.err.println("lazyAnts after unseen " + lazyAnts.size());
	    
        // unblock hills
        for (Tile myHill : ants.getMyHills()) {
            if (ants.getMyAnts().contains(myHill) && lazyAnts.contains(myHill)) {
                for (Aim direction : Aim.values()) {
                    if (doMoveDirection(myHill, direction)) {
                        break;
                    }
                }
            }
        }
        
        if (unseendebug)
        	System.err.println("lazyAnts after unblock " + lazyAnts.size());

        if (ants.getMyHills().iterator().hasNext())
        {
	        Tile firstHill = ants.getMyHills().iterator().next();
	        Set<Tile> rallyPoints = new HashSet<Tile>();
	        for (int i=10;i<=ants.getCols();i+=10)
	        	for (int j=10;j<=ants.getRows();j+=10)
		        {
	        		Tile newMove = new Tile(j,i);
	        		Tile newLoc = ants.getTile(firstHill,newMove);
	        		if (unseenTiles.contains(newLoc))
	        			rallyPoints.add(newLoc);
	        		
	        		if (rallyPoints.size()>10)
	        		{
	        			i=999;
	        			j=999;
	        		}
	        		// should really check if near other hills and not add
		        }
	        
	        if (rallyPoints.size()<10)
	        {
	        	for (Tile unseenLoc : unseenTiles)
	        	{
	        		rallyPoints.add(unseenLoc);
	        		if (rallyPoints.size()>10)
	        		{
	        			break;
	        		}
	        	}
	        }

	        for (Tile antLoc : lazyAnts.toArray(new Tile[0])) {
				if (ants.getTimeRemaining()<100)
				{
					if (timing)
						System.err.println("Low remaining time giving up 3");
					break;
				}

	            List<Route> unseenRoutes = new ArrayList<Route>();
	            for (Tile unseenLoc : rallyPoints) {
	            	int distance=999;
	           		distance = ants.getDistance2(antLoc, unseenLoc);
	            		
	                Route route = new Route(antLoc, unseenLoc, distance);
	                unseenRoutes.add(route);
					if (ants.getTimeRemaining()<100)
					{
						if (timing)
							System.err.println("Low remaining time giving up 2");
						break;
					}
	            }
	            Collections.sort(unseenRoutes);
	            for (Route route : unseenRoutes) {
					if (loading)
						System.err.println("before");
	                if (doMoveLocation(route.getStart(), route.getEnd())) {
						if (loading)
							System.err.println("after1");
	                        break;
	                }
					if (loading)
						System.err.println("after2");
	                    break;
	            }

	            /*
		        List<Aim> directions = ants.findNearest(antLoc, rallyPoints);
		        for (Aim direction : directions) {
		            if (doMoveDirection(antLoc, direction)) {
		    			//System.err.println("Take the move " + direction);
		                break;
		            }
		        }
		        */
	        }
        }
	        
        if (unseendebug)
        	System.err.println("lazyAnts after rally " + lazyAnts.size());
        
        for (Tile antLoc : new ArrayList<Tile>(lazyAnts)) {
    			List<Aim> directions = new ArrayList<Aim>(EnumSet.allOf(Aim.class));
    			Collections.shuffle(directions);
    			Aim wheremin=Aim.NORTH;
    			int mincount=999;
    			for (Aim direction : directions) {
        			int count=0;
    				Tile newLoc=antLoc;
    				for (int i=0 ; i<10 ; i++){
    			        newLoc = ants.getTile(newLoc, direction);
    			        if (!ants.getIlk(newLoc).isUnoccupied()) {
    			        	count++;
    			        }
    				}
    				if (count<mincount)
    				{
    					mincount=count;
    					wheremin=direction;
    				}
    			}
                if (doMoveDirection(antLoc, wheremin)) {
                    //break;
                }
        }
        
        if (unseendebug)
        	System.err.println("lazyAnts after random " + lazyAnts.size());
        
    	if (timing)
    	{	
    		System.err.println("After rest " + ants.getTimeRemaining() + " took " + (time_r-ants.getTimeRemaining()));
    		time_r=ants.getTimeRemaining();
    	}

    }

    //@Override
    public void doTurnold2() {
        Ants ants = getAnts();
        orders.clear();

        //  default move
        for (Tile myAnt : ants.getMyAnts()) {
            for (Aim direction : Aim.values()) {
                if (doMoveDirection(myAnt, direction)) {
                    break;
                }
            }
        }
    }

    /**
     * For every ant check every direction in fixed order (N, E, S, W) and move it if the tile is
     * passable.
     */
    //@Override
    public void doTurnold() {
        Ants ants = getAnts();
        for (Tile myAnt : ants.getMyAnts()) {
            for (Aim direction : Aim.values()) {
                if (ants.getIlk(myAnt, direction).isPassable()) {
                    ants.issueOrder(myAnt, direction);
                    break;
                }
            }
        }
    }
}
