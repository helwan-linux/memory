# Maintainer: Saeed Badreldin <saeed@helwanlinux.org>

pkgname=hel-memory
pkgver=1.0.0
pkgrel=1
pkgdesc="Ultimate memory game for Helwan Linux"
arch=('x86_64')
url="https://github.com/helwan-linux/memory"
license=('MIT')
depends=('python' 'python-pygame')

source=("git+https://github.com/helwan-linux/memory.git")
sha256sums=('SKIP')

package() {
    cd "memory"
    
    install -Dm755 "Memory.py" \
        "$pkgdir/usr/bin/hel-memory"

    install -Dm644 "hel-memory.png" \
        "$pkgdir/usr/share/pixmaps/hel-memory.png"

    install -Dm644 "hel-memory.desktop" \
        "$pkgdir/usr/share/applications/hel-memory.desktop"
}
