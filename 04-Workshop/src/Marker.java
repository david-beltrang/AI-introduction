import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;

public class Marker implements IGameObject{

    private BufferedImage marker;
    private int x;
    private int y;
    private int type;

    private boolean won=false;
    private float alpha= 1;
    private float fadeSpeed = 0.1f;

    // Crea un marcador en la posición especificada (x, y) con el tipo especificado (0 para "X" y 1 para "O"), cargando la imagen correspondiente para el marcador
    public Marker(int x, int y, int type){
        this.x = x;
        this.y = y;
        this.type = type % 2;
        String markerType = this.type == 0 ? "x" : "o";
        try {
                marker = ImageIO.read(new File("04-Workshop/assets/" + markerType + ".png"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Actualiza el estado del marcador, manejando la animación de parpadeo si el marcador forma parte de una combinación ganadora
    @Override
    public void update(float deltaTime) {
        if(won){
            alpha += fadeSpeed;
            if(alpha >= 1f){
                alpha = 1f;
                fadeSpeed *= -1;
                return;
            } else if (alpha <= 0.5f){
                alpha = 0.5f;
                fadeSpeed *= -1;
                return;
            }
        }
    }

    // Renderiza el marcador, dibujando la imagen del marcador en la posición correspondiente en el tablero, aplicando una animación de parpadeo si el marcador forma parte de una combinación ganadora
    @Override
    public void render(Graphics2D graphicsRender) {

        AlphaComposite ac = AlphaComposite.getInstance(AlphaComposite.SRC_OVER, alpha);
        graphicsRender.setComposite(ac);

        int size = Main.WIDTH / Main.ROWS;
        graphicsRender.drawImage(marker, x*size, y*size, size, size, null);

        ac = AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 1);
        graphicsRender.setComposite(ac);
    }

    public int getType() {
        return type;
    }

    public void setWon(boolean won) {
        this.won = won;
    }
}
