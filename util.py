'''
ASSIGNMENT 2: HUFFMAN CODING
Melisse Doroteo - 1499913
Raymond Sarinas - 14???????
'''

import bitio
import huffman


def read_tree(bitreader):
    '''Read a description of a Huffman tree from the given bit reader,
        and construct and return the tree. When this function returns, the
        bit reader should be ready to read the next bit immediately
        following the tree description.

        Huffman trees are stored in the following format:
        * TreeLeaf is represented by the two bits 01, followed by 8 bits
        for the symbol at that leaf.
        * TreeLeaf that is None (the special "end of message" character)
        is represented by the two bits 00.
        * TreeBranch is represented by the single bit 1, followed by a
        description of the left subtree and then the right subtree.

        Args:
        bitreader: An instance of bitio.BitReader to read the tree from.

        Returns:
        A Huffman tree constructed according to the given description.
    '''
    # check the first bit
    firstbit = bitreader.readbit()

    if firstbit == 0: # if 0, leaf.
        secondbit = bitreader.readbit() # check second bit

        if secondbit == 0: # if leaf is '00', then EOM
            return huffman.TreeLeaf(None)
        else: # if leaf is '01', then get those bytes sis
            return huffman.TreeLeaf(bitreader.readbits(8))

    else: # otherwise first bit should be a 1, so it's a branch i guess
        # return the children! (left and right)
        left = read_tree(bitreader)
        right = read_tree(bitreader)
        return huffman.TreeBranch(left, right)


def decode_byte(tree, bitreader):
    """
        Reads bits from the bit reader and traverses the tree from
        the root to a leaf. Once a leaf is reached, bits are no longer read
        and the value of that leave is returned.

        Args:
        bitreader: An instance of bitio.BitReader to read the tree from.
        tree: A Huffman tree.

        Returns:
        Next byte of the compressed bit stream.
    """

    while True:
        if isinstance(tree, huffman.TreeBranch):
            # if currently transversing a branch, then check if child/node
            # either move to the left or right subbranch/child/node
                bit = bitreader.readbit()

                if bit == 0:
                    tree = tree.left
                elif bit == 1:
                    tree = tree.right

        elif isinstance(tree, huffman.TreeLeaf):
        # when transversing tree and get to a leaf, then just return its value
            return tree.value

        else:
            # raise a type error if whatever it is that got inputted isn't a tree
            raise TypeError(type(tree), 'is not a tree!')


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
        read_tree function. Then use that tree to decode the rest of the
        stream and write the resulting symbols to the 'uncompressed'
        stream.

        Args:
        compressed: A file stream from which compressed input is read.
        uncompressed: A writable file stream to which the uncompressed
        output is written.
    '''

    # get bits from compressed file stream and use it to get tree
    inputstream = bitio.BitReader(compressed)
    # notcompressed = bitio.BitWriter(uncompressed)
    tree = read_tree(inputstream)

    while True: # repeatedly read coded bits from file and decode them using tree
        decoded_bytes = decode_byte(tree, inputstream)
        if decoded_bytes == None:
            break

        # write bits to uncompressed file
        uncompressed.write(bytes([decoded_bytes]))
        # notcompressed.writebits(decoded_bytes, 8) <-- this makes it too slow



def write_tree(tree, bitwriter):
    '''Write the specified Huffman tree to the given bit writer.  The
        tree is written in the format described above for the read_tree
        function.

        DO NOT flush the bit writer after writing the tree.

        Args:
        tree: A Huffman tree.
        bitwriter: An instance of bitio.BitWriter to write the tree to.
    '''
    if type(tree) == huffman.TreeLeaf:
        if tree.value == None:  # checks if the value is none
            bitwriter.writebit(0)  # writes "00"
            bitwriter.writebit(0)
        else:
            bitwriter.writebit(0)  # writes 01
            bitwriter.writebit(1)
            huffman.TreeLeaf(bitwriter.writebits(tree.value, 8))
            # writes the next 8 bits that should come after 01
            
    elif type(tree) == huffman.TreeBranch:
        # Writes the single bit 1, followed by a description of the left subtree and then the right subtree.
        bitwriter.writebit(1)
        left = write_tree(tree.left, bitwriter)
        right = write_tree(tree.right, bitwriter)
    # else:
    #     pass



def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
        write_tree function. Then use the same tree to encode the data
        from the input stream 'uncompressed' and write it to 'compressed'.
        If there are any partially-written bytes remaining at the end,
        write 0 bits to form a complete byte.

        Flush the bitwriter after writing the entire compressed file.

        Args:
        tree: A Huffman tree.
        uncompressed: A file stream from which you can read the input.
        compressed: A file stream that will receive the tree description
        and the coded input data.
    '''

    compressedStream = bitio.BitWriter(compressed)     # writes the ouput stream(compressed) in binary mode
    uncompStream = bitio.BitReader(uncompressed)       # reads the input stream(uncompressed) in binary mode
    enctable = huffman.make_encoding_table(tree)       # creates the encoding table
    write_tree(tree, compressedStream)                 # get tree encoding table

    # reads each entry of the encoding table till we hit the EOF
    while True:
        # read 8 bits
        try:
            read = uncompStream.readbits(8)
            # stores it in encoding table
            comptable = enctable[read]
            for bit in comptable:
                compressedStream.writebit(bit)
        # when eof occurs, break from loop
        except EOFError:
            comptable = enctable[None]
            print("EOF")
            break

    compressedStream.flush()
