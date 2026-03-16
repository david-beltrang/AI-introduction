import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Image;

import javax.swing.JPanel;

public class Panel extends JPanel implements Runnable{
    // Thread used to run our game on
    private Thread thread;

    // Will be our graphics renderer to render our scene
    protected Graphics2D graphicsRender;

    // Used as reference to generate graphics renderer, we will basically render everything to this image
    private Image img;

    // Background color as base background so it's not only white
    private Color backgroundColor;

    public Panel(Color color) {
        this.backgroundColor = color;

        setPreferredSize(new Dimension(Main.WIDTH, Main.HEIGHT));
        setFocusable(false);
        requestFocus();
    }

    @Override
    public void addNotify() {
        super.addNotify();

        if(thread == null){
            thread = new Thread(this);
            thread.start();
        }
    }

    @Override
    public void run() {
        init(); // We will initialize the loop before it runs

        // Get current time
        long lastTime = System.nanoTime();

        // 1 second to nanosecond divided by total frames per second
        double nanoSecondPerUpdate = 1000000000D / 30;

        // Delta time to pass nanosecond between ticks/frames
        float deltaTime = 0;

        while(true){
            // Get current nanosecond
            long now = System.nanoTime();
            // Calculate delta time based on our desired frames per second
            deltaTime += (now - lastTime) / nanoSecondPerUpdate;
            // Set last time to current time for next calculation
            lastTime = now;

            if(deltaTime >= 1){
                // Tick + delta time
                update(deltaTime);

                // Render
                render();

                // Reset delta
                deltaTime--;
            }

            try {
                // Sleep thread to run code
                Thread.sleep(1);
            } catch (InterruptedException e) {
                // If anything goes wrong, we see what went wrong by this exception trace
                e.printStackTrace();
            }
        }
    }

    public void init() {
        // Generate image to collect graphics from
        img = createImage(Main.WIDTH, Main.HEIGHT);
        graphicsRender = (Graphics2D) img.getGraphics();
    }

    public void update(float deltaTime) {
        // This will be used by our child class
    }

    public void render() {
        // Set rendering configuration
        graphicsRender.clearRect(0, 0, Main.WIDTH, Main.HEIGHT);
        graphicsRender.setFont(new Font("Arial", Font.CENTER_BASELINE, 25));

        // Set color for background
        graphicsRender.setColor(backgroundColor);
        // Draw background
        graphicsRender.fillRect(0, 0, Main.WIDTH, Main.HEIGHT);
        // Reset color to white so not everything is colored as our
        // Background color
        graphicsRender.setColor(Color.white);
    }

    public void clear(){
        Graphics graphics = getGraphics();

        if(img != null) {
            // Draw final image
            graphics.drawImage(img, 0, 0, null);
        }

        // Dispose image to redraw
        graphics.dispose();
    }
}