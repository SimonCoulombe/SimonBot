
/**
 * Represents a tile of the game map.
 */
public class Tile implements Comparable<Tile> {
    private int row;
    
    private int col;
    
    private Tile next = null;
    
    private static Tile tileCache = null;
    
    public static Tile getTile(int row, int col)
    {
    	if (tileCache!=null)
    	{
    		Tile ret = tileCache;
    		tileCache = ret.next; // could be null thats fine
        	ret.init(row, col);
    		return ret;
    	}
    	else
    	{
    		return new Tile(row, col);
    	}
    }
    
    public void done()
    {
    	this.next=tileCache; // could be null thats fine
    	tileCache=this;
    }
    
    public Tile copyof()
    {
    	return getTile(this.getRow(), this.getCol());
    }
    
    /**
     * Creates new {@link Tile} object.
     * 
     * @param row row index
     * @param col column index
     */
    public Tile(int row, int col) {
    	init(row, col);
    }
    
    private void init(int row, int col)
    {
        this.row = row;
        this.col = col;
    }
    
    /**
     * Returns row index.
     * 
     * @return row index
     */
    public int getRow() {
        return row;
    }
    
    /**
     * Returns column index.
     * 
     * @return column index
     */
    public int getCol() {
        return col;
    }
    
    /** 
     * {@inheritDoc}
     */
    @Override
    public int compareTo(Tile o) {
        return hashCode() - o.hashCode();
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public int hashCode() {
        return row * Ants.MAX_MAP_SIZE + col;
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public boolean equals(Object o) {
        boolean result = false;
        if (o instanceof Tile) {
            Tile tile = (Tile)o;
            result = row == tile.row && col == tile.col;
        }
        return result;
    }
    
    /**
     * {@inheritDoc}
     */
    @Override
    public String toString() {
        return row + " " + col;
    }
}
