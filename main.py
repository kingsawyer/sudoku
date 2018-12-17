from collections import Counter

class Square(object):
    def __init__(self, val, x, y):
        self.val = int(val) if val != ' ' else ' '
        self.nines = []
        self.possibles = set(range(1,10)) if val == ' ' else set(val)
        self.x = x
        self.y = y

    def add_nine(self, nine):
        self.nines.append(nine)

    def set(self, val):
        print('setting {}, {} to {}'.format(self.x, self.y, val))
        self.val = val
        self.possibles = {val}
        for nine in self.nines:
            for square in nine:
                if square != self:
                    square.possibles.discard(val)

class Solver(object):
    def __init__(self):
        self.solved_nines = []

    def print_nines(self):
        print('--------')
        for z in self.nines:
            print(','.join(str(x.val) for x in z))
    def print_board(self):
        i = 0
        print('-' * 60)
        for x in range(9):
            for y in range(9):
                square = self.squares[i]
                i += 1
                if square.val == ' ':
                    if len(square.possibles) < 6:
                        print (''.join([str(x) for x in list((square.possibles))]) + ' ' * (7 - len(square.possibles)), end = '')
                    else:
                        print ('   -   ', end = '')
                else:
                    print('   ' + str(square.val) + '   ', end = '')
            print('')
        print('-' * 60)

    def read_board(self):
        self.nines = []
        test_board = ('75  9   2'
                      '   4 7   '
                      '  3 2   6'
                      ' 3    9  '
                      '   6 1   '
                      '  8    7 '
                      '5   6 1  '
                      '   9 5   '
                      '1   8  24')
        # test_board = (' 7    652'
        #               '8    2 1 '
        #               '    4    '
        #               ' 9 3  4 1'
        #               '  2   7  '
        #               '1 8  5 2 '
        #               '    3    '
        #               ' 3 6    9'
        #               '986    3 ')
        # test_board = ('72    6  '
        #               '       37'
        #               '  39   2 '
        #               '   2598  '
        #               '    7    '
        #               '  9468   '
        #               ' 8   57  '
        #               '56       '
        #               '  2    95')
        self.squares = [Square(val, i % 9, i // 9) for i, val in enumerate(test_board)]
        for i in range(9):
            row = []
            for j in range(9):
                row.append(self.squares[i*9 + j])
            self.nines.append(row)
        for i in range(9):
            col = []
            for j in range(9):
                col.append(self.squares[i + j*9])
            self.nines.append(col)
        for i in range(3):
            for j in range(3):
                square = []
                for l in range(3):
                    for m in range(3):
                        square.append(self.squares[i*3 + j*3*9 + l + m * 9])
                self.nines.append(square)
        for nine in self.nines:
            for square in nine:
                square.add_nine(nine)
        self.set_possibles()
        self.print_board()

        while(True):
            if self.check_possibles():
                continue
            if self.check_solos():
                continue
            if self.set_exclude():
                continue
            if self.one_nine():
                continue
            # if self.check_duos():
            #     continue
            # if self.set_exclude_n(3):
            #     continue
            # if self.check_mins(3):
            #     continue
            # if self.set_exclude_n(4):
            #     continue
            # if self.check_mins(4):
            #     continue
            break
        self.print_board()

    def set_possibles(self):
        """ Part of setup, set initial possibles from known squares"""
        for square in self.squares:
            if square.val != ' ':
                square.set(square.val)

    def check_possibles(self):
        """If a square has only 1 possible, set the value to it"""
        found_something = False
        for square in self.squares:
            if square.val == ' ' and len(square.possibles) == 1:
                new_val = next(iter(square.possibles))
                print("found single!")
                found_something = True
                for cn in square.nines:
                    for cns in cn:
                        if cns != square:
                            assert cns.val != new_val
                square.set(new_val)
        return found_something

    def check_solos(self):
        """If a square in a nine has the only possible spot for a value, set the value to it"""
        found_something = False
        for nine in self.nines:
            if nine in self.solved_nines:
                continue
            count = Counter()
            for square in nine:
                if len(square.possibles) > 1:
                    count.update(square.possibles)
            most_common = count.most_common()
            if most_common:
                least_element, least_count = most_common[-1]
                if least_count == 1:
                    print('found solo')
                    found_something = True
                    for square in nine:
                        if least_element in square.possibles:
                            for cn in square.nines:
                                for cnq in cn:
                                    assert cnq.val != least_element
                            square.set(least_element)
                            break
                    else:
                        assert False, 'should have found it'
            else:
                self.solved_nines.append(nine)
        return found_something

    def check_duos(self):
        """If only two squares have places for two values, narrow the set to those two values"""
        found_something = False
        for nine in self.nines:
            if nine in self.solved_nines:
                continue
            count = Counter()
            for square in nine:
                if len(square.possibles) > 1:
                    count.update(square.possibles)
            most_common = count.most_common()
            if len(most_common) > 2:
                least_element1, least_count1 = most_common[-1]
                least_element2, least_count2 = most_common[-2]
                found_squares = []
                if least_count2 == 2:
                    assert least_count1 == 2
                    for square in nine:
                        if least_element1 in square.possibles and least_element2 in square.possibles:
                            found_squares.append(square)
                    if len(found_squares) == 2:
                        for square in found_squares:
                            if len(square.possibles) > 2:
                                found_something = True
                                print('found duo')
                                square.possibles = {least_element1, least_element2}
        return found_something

    def check_mins(self, size):
        """General form of check_solos"""
        found_something = False
        for nine in self.nines:
            if nine in self.solved_nines:
                continue
            count = Counter()
            for square in nine:
                if len(square.possibles) > 1:
                    count.update(square.possibles)
            most_common = count.most_common()
            if len(most_common) > size and most_common[-size][1] == size:
                least_elements = set(least_element for least_element, _ in most_common[-size:])
                found_squares = []
                for square in nine:
                    if least_elements.intersection(square.possibles):
                        found_squares.append(square)
                if len(found_squares) == size:
                    for square in found_squares:
                        if len(square.possibles) > size:
                            found_something = True
                            print('found min count match')
                            square.possibles = set(least_elements)
        return found_something

    def one_nine(self):
        """If all the places for a value in one nine also are entirely in another nine, then exclude the value from the other places in the other"""
        found_something = False
        for nine in self.nines:
            for val in range(1,10):
                other_nines = []
                all_squares = set()
                for square in nine:
                    if square.val == ' ' and val in square.possibles:
                        other_nines.extend(square.nines)
                        all_squares.add(square)
                for other_nine in other_nines:
                    if other_nine == nine:
                        continue
                    if all(x in other_nine for x in all_squares):
                        for square in other_nine:
                            if square not in nine and val in square.possibles:
                                print('found nine intersect')
                                square.possibles.remove(val)
                                found_something = True
        return found_something

    def set_exclude(self):
        """ If 2 squares in a nine have the same two value set, exclude those values from the other squares in the nine"""
        found_something = False
        for nine in self.nines:
            if nine in self.solved_nines:
                continue
            for nsquare_i, square1 in enumerate(nine):
                if len(square1.possibles) == 2:
                    for square2 in nine[nsquare_i+1:]:
                        if square2.possibles == square1.possibles:
                            for other in nine:
                                if other != square1 and other != square2 and len(other.possibles) > 1:
                                    if square1.possibles.intersection(other.possibles):
                                        print('found set exclude')
                                        other.possibles.difference_update(square1.possibles)
                                        # return True
                                        assert len(other.possibles) > 0
                                        found_something = True
        return found_something

    def _set_exclude_n_r(self, nine, size, current_set, current_possibles, current_i):
        found_something = False
        for square in nine[current_i+1:]:
            current_i += 1
            if len(square.possibles) < 2 or len(square.possibles) > size:
                continue
            new_possibles = current_possibles | square.possibles
            if len(new_possibles) <= size:
                old_possibles = set(current_possibles)
                current_set.add(square)
                current_possibles = new_possibles
                if len(current_set) == size:
                    # remove from others
                    for exclude_square in nine:
                        if exclude_square not in current_set and len(exclude_square.possibles.intersection(current_possibles)):
                            found_something = True
                            print('found set_n exclude')
                            exclude_square.possibles.difference_update(current_possibles)
                else:
                    if self._set_exclude_n_r(nine, size, current_set, current_possibles, current_i):
                        return True
                current_set.remove(square)
                current_possibles = old_possibles
        return found_something

    def set_exclude_n(self, size):
        for nine in self.nines:
            if nine in self.solved_nines:
                continue
            if self._set_exclude_n_r(nine, size, set(), set(), -1):
                return True

        return False



if __name__ == '__main__':
    solver = Solver()
    solver.read_board()