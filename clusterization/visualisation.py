from PIL import Image, ImageDraw


__author__ = '4ikist'


class hierarchy_vis():
    @staticmethod
    def print_clust(clust, label=None, n=0):
        for i in range(n): print ' ',
        if clust.id < 0:
            print '-'
        else:
            if not label:
                print clust.id
            else:
                print label[clust.id]
        if clust.left: hierarchy_vis.print_clust(clust.left, label=label, n=n + 1)
        if clust.right: hierarchy_vis.print_clust(clust.right, label=label, n=n + 1)

    @staticmethod
    def draw_dendogram(cluster, labels, jpeg='clusters.jpg'):

        def get_cluster_heigh(cluster):
            if not cluster.left and not cluster.right: return 1
            return get_cluster_heigh(cluster.left) + get_cluster_heigh(cluster.right)


        def get_cluster_depth(cluster):
            if not cluster.left and not cluster.right: return 0
            return max(get_cluster_depth(cluster.left), get_cluster_depth(cluster.right)) + cluster.distance


        def draw_node(draw, clust, x, y, scaling, labels):
            if clust.id < 0:
                h1 = get_cluster_heigh(clust.left) * 20
                h2 = get_cluster_heigh(clust.right) * 20
                top = y - (h1 + h2) / 2
                bottom = y + (h1 + h2) / 2
                ll = clust.distance * scaling
                draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill=(255, 0, 0))
                draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill=(255, 0, 0))
                draw.line((x, bottom - h2 / 2, x + ll, bottom - h2 / 2), fill=(255, 0, 0))
                draw_node(draw, clust.left, x + ll, top + h1 / 2, scaling, labels)
                draw_node(draw, clust.right, x + ll, bottom - h2 / 2, scaling, labels)
            else:
                draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))

        h = get_cluster_heigh(cluster) * 20
        w = 1200
        depth = get_cluster_depth(cluster)
        scaling = float(w - 150) / depth
        img = Image.new('RGB', (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.line((0, 10, h / 2, h / 2), fill=(255, 0, 0))
        draw_node(draw, cluster, 10, h / 2, scaling, labels)
        img.save(jpeg, 'JPEG')

