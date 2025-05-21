from pylab import *


def make_N_colors(N):
    cdict = {'red': ((0.0, 0.9, 0.9),
                     (0.5, 0.1, 0.1),
                     (1.0, 0.0, 0.0)),
             'green': ((0.0, 0.9, 0.9),
                       (0.5, 0.8, 0.8),
                       (1.0, 0.1, 0.1)),
             'blue': ((0.0, 0.0, 0.0),
                      (0.5, 0.4, 0.4),
                      (1.0, 0.7, 0.7))}
    my_cmap = matplotlib.colors.LinearSegmentedColormap(
        'my_colormap', cdict, N)
    return my_cmap(arange(N))


def make_colormap(N):
    cdict = {'red': ((0.0, 0.0, 0.0),
                     (0.56, 0.0, 0.0),
                     (1.0, 1.0, 1.0)),
             'green': ((0.0, 0.0, 0.0),
                       (0.56, 0.553, 0.553),
                       (1.0, 1.0, 1.0)),
             'blue': ((0.0, 0.5, 0.5),
                      (0.56, 0.322, 0.322),
                      (1.0, 0.0, 0.0))}
    return matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, N)


ygb_cmap = make_colormap(256)

if __name__ == "__main__":
    N = 256
    my_cmap = make_colormap(N)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    figure()
    imshow(gradient, aspect='auto', cmap=my_cmap)

    figure()
    import matplotlib.cbook as cbook
    # data are 256x256 16 bit integers
    dfile = cbook.get_sample_data(
        '/usr/share/matplotlib/sample_data/s1045.ima.gz')
    im = np.fromstring(dfile.read(), np.uint16).astype(float)
    im.shape = 256, 256

    # imshow(im, ColormapJet(256))
    imshow(im, cmap=my_cmap)
    axis('off')

    show()
