# Maintainer: Saeed Badreldin <saeed@helwanlinux.org>

pkgname=hel-memory
pkgver=1.0.0
pkgrel=1
pkgdesc="Classic Memory card game for Helwan Linux"
arch=('any')
license=('GPL-3.0-or-later')
depends=('python' 'python-pygame')
source=(
    "Memory.py"
    "hel-memory.desktop"
    "hel-memory.png"
)
sha256sums=('SKIP' 'SKIP' 'SKIP')

package() {
    install -Dm755 "Memory.py" \
        "$pkgdir/usr/share/helwan-games/hel-memory/Memory.py"

    install -Dm644 "hel-memory.desktop" \
        "$pkgdir/usr/share/applications/hel-memory.desktop"

    install -Dm644 "hel-memory.png" \
        "$pkgdir/usr/share/icons/hicolor/256x256/apps/hel-memory.png"

    install -Dm755 /dev/stdin \
        "$pkgdir/usr/bin/hel-memory" <<'EOF'
#!/bin/sh
exec python /usr/share/helwan-games/hel-memory/Memory.py "$@"
EOF
}
