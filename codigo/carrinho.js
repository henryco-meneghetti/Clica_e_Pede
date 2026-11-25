/*
 * Trecho do catálogo do Clica & Pede (versão simplificada).
 *
 * Carrinho com quantidade, salvo no navegador, e envio do pedido
 * já formatado para o WhatsApp da loja.
 */

let carrinho = carregar("catalogo_cart", []);

function carregar(chave, padrao) {
    try { return JSON.parse(localStorage.getItem(chave)) || padrao; }
    catch (e) { return padrao; }
}

function salvar(chave, valor) {
    try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) { }
}

// O mesmo produto pode ser vendido por unidade ou por pacote
function adicionarAoCarrinho(produto, tipo = "unidade") {
    const porPacote = tipo === "pacote" && produto.pack;
    const preco = porPacote ? produto.pack.price : produto.unitPrice;
    const rotulo = porPacote
        ? `${produto.pack.type} (${produto.pack.quantity} un)`
        : "un";

    const item = carrinho.find(i => i.id === produto.id && i.tipo === tipo);
    if (item) {
        item.quantidade++;
    } else {
        carrinho.push({ id: produto.id, nome: produto.name, tipo, rotulo, preco, quantidade: 1 });
    }
    salvar("catalogo_cart", carrinho);
}

function mudarQuantidade(id, tipo, delta) {
    const item = carrinho.find(i => i.id === id && i.tipo === tipo);
    if (!item) return;

    item.quantidade += delta;
    if (item.quantidade <= 0) {
        carrinho = carrinho.filter(i => i !== item);
    }
    salvar("catalogo_cart", carrinho);
}

function totalDoCarrinho() {
    return carrinho.reduce((total, item) => total + item.preco * item.quantidade, 0);
}

// Monta a mensagem e abre o WhatsApp da loja com o pedido pronto
function enviarPedidoWhatsApp(telefoneDaLoja) {
    if (carrinho.length === 0) return;

    let mensagem = "Olá! Gostaria de solicitar um orçamento para:\n\n";
    carrinho.forEach(item => {
        mensagem += `- ${item.quantidade}x ${item.nome} (${item.rotulo})\n`;
    });
    mensagem += "\nAguardo retorno.";

    const telefone = telefoneDaLoja.replace(/\D/g, "");
    window.open(`https://wa.me/${telefone}?text=${encodeURIComponent(mensagem)}`, "_blank");
}
