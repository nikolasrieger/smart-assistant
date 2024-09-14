from engine.vision_engine.screen_handler import ScreenHandler
from PIL import Image
from torch import no_grad, cuda, stack, argmax
from clip import load, tokenize
from cv2 import rectangle, imwrite
from numpy import array

class ScreenAnalyzer():
    def __init__(self):
        self.__device = "cuda" if cuda.is_available() else "cpu"
        self.__model, self.__preprocess = load("ViT-B/32", device=self.__device)

    def analyze_image(self, image: Image, text_prompts: list[str]):
        text = tokenize(text_prompts).to(self.__device)
        patches, positions = self.__extract_patches(image)
        patch_tensors = stack([self.__preprocess(Image.fromarray(patch)).to(self.__device) for patch in patches])
        with no_grad():
            patch_features = self.__model.encode_image(patch_tensors)
        with no_grad():
            text_features = self.__model.encode_text(text)
        similarities = (patch_features @ text_features.T).softmax(dim=-1)
        best_patch_per_prompt = argmax(similarities, dim=0)
        best_positions = []
        for i, prompt in enumerate(text_prompts):
            best_patch_idx = best_patch_per_prompt[i]
            best_position = positions[best_patch_idx.item()]
            max_similarity = similarities[best_patch_idx, i].item()
            best_positions.append({"position": best_position, "similarity": max_similarity})
        return best_positions
    
    def __save_image(self, image: Image, positions: list[dict], text_prompts: list[str], best_patch_idx: int):
            img_np = array(image)
            best_position = positions[best_patch_idx.item()]
            x1, y1, x2, y2 = best_position
            img_with_box = rectangle(img_np.copy(), (x1, y1), (x2, y2), (255, 255, 255), 5)
            imwrite("image_{}.png".format(i), img_with_box)

    def __extract_patches(self, image: Image, patch_size: int = 64, stride: int = 32):
        image = array(image)
        patches = []
        positions = []
        for y in range(0, image.shape[0] - patch_size + 1, stride):
            for x in range(0, image.shape[1] - patch_size + 1, stride):
                patch = image[y:y + patch_size, x:x + patch_size]
                patches.append(patch)
                positions.append((x, y, x + patch_size, y + patch_size))
        return patches, positions
    
if __name__ == "__main__":
    screen_handler = ScreenHandler()
    screen = screen_handler.get_active_screen()
    screen_analyzer = ScreenAnalyzer()
    screen_analyzer.analyze_image(screen)