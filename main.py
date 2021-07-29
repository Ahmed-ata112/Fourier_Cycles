from manim import *
import numpy as np
from svgpathtools import *


class FourierVis(VMobject):

    def __init__(
            self, complex_points, num_coeffs, rate=1., **kwargs):
        super().__init__(**kwargs)
        self.complex_points = complex_points
        self.N = len(self.complex_points)
        self.K = num_coeffs
        self.rate = .1 * rate * self.N
        self.circles = VGroup()
        self.Arrows = VGroup()

        # Create Back Path
        self._create_background()
        # Process Tht circles and Vectors
        self._process_cycles()
        # Draw Path
        self._draw_path()

    def _create_background(self):
        real_points = list(map(complex_to_R3, self.complex_points))
        self.path = VMobject(
            stroke_color=GRAY_C, stroke_width=1, stroke_opacity=1
        ).set_points_as_corners([real_points[-1], *real_points])  # Creates Mobj with the corner points as path

        self.add(self.path)
        return self

    def _process_cycles(self):
        def create_one_cycle(radius, angle):
            circle = Circle(radius=radius,
                            stroke_color=BLUE_E,
                            stroke_width=1)
            arrow = Arrow(ORIGIN, circle.get_right(),
                          buff=100,
                          stroke_color=WHITE,
                          stroke_width=3)
            return VDict([("circle", circle), ("arrow", arrow)]).rotate(angle)

        # TODO: Create your own Fourier Function
        fft = np.fft.fft(self.complex_points) / self.N  # we divide because it is computed on the whole Range and we
        # want only a unit (0 -> 1)
        self.cycles = VGroup(VDict([("arrow", Dot(radius=0))]))

        for index, f in enumerate(
                [int(i / 2) * ((-1) ** i) for i in range(1, self.K + 1)]):  # 0 1 -1 2 -2 3 -3 4 -4 ... nice
            cycle = create_one_cycle(radius=abs(fft[f]), angle=np.angle(fft[f]))
            cycle.set(previous=self.cycles[index]["arrow"].get_end)
            cycle.set(speed=TAU * f / self.N)
            cycle.add_updater(
                lambda mobj, dt: mobj.move_to(mobj.previous()).rotate(mobj.speed * dt * self.rate))
            self.cycles.add(cycle)
            self.circles.add(cycle["circle"])
            self.Arrows.add(cycle["arrow"])
        self.add(self.cycles)
        return self

    def _draw_path(self):
        self.pathie = TracedPath(self.cycles[-1]["arrow"].get_end, min_distance_to_new_point=.01,
                                 stroke_color=GREEN_A, stroke_width=2)
        self.add(self.pathie)
        return self


class CreateFourier(Scene):
    def construct(self):
        # get an array of complex points
        N = 100

        def get_shape_from_Tex(tex):
            path = VMobject()
            for sp in Tex(tex).family_members_with_points():
                path.append_points(sp.get_points())
                complex_points = np.array(
                    [complex(*path.point_from_proportion(alpha)[:2]) for alpha in np.arange(0, 1, 1 / N)]) * 16
            return complex_points

        def get_shape_from_svg():
            fname = r'src\star.svg'
            paths, attributes = svg2paths(fname)
            complex_points = []
            for path, attr in zip(paths, attributes):
                pathLength = path.length()
                numSamples = int(pathLength * 1)
                for i in range(numSamples):
                    complex_points.append(path.point(path.ilength(pathLength * i / (numSamples - 1))))

            return complex_points


        # tex = r"$\Lambda$"
        # complex_points = np.array(get_shape_from_Tex(tex))
        complex_points = np.array(get_shape_from_svg())
        complex_points = (complex_points - np.mean(complex_points)) / np.max(abs(complex_points)) * 4
        sh = FourierVis(complex_points, num_coeffs=50)
        self.add(sh)
        self.wait(2 * TAU)

